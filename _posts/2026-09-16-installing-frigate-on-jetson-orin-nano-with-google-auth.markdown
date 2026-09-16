---
layout: post
title:  "Building an Edge AI NVR: Installing Frigate 0.18 on Jetson Orin Nano with Google Authentication"
date:   2026-09-16 18:30:00 +0530
author: "Prakritish Sen Eshore"
description: "Complete guide to deploying Frigate NVR 0.18 on NVIDIA Jetson Orin Nano with sub-10ms TensorRT YOLOv7 detection, ArcFace face recognition, and Google SSO via OAuth2-Proxy and HAProxy."
image: /assets/images/frigate-jetson-orin-nano.jpg
categories: devops frigate jetson edge-ai security
tags: devops frigate jetson-orin-nano google-oauth oauth2-proxy haproxy tensorrt
---

![Edge AI NVR Surveillance with NVIDIA Jetson Orin Nano and Google Authentication](/assets/images/frigate-jetson-orin-nano.jpg)

## Introduction
In this guide, we will deploy a production-grade, hardware-accelerated Frigate NVR 0.18 stack on the NVIDIA Jetson Orin Nano (8GB) and secure it behind Google Authentication using HAProxy and OAuth2-Proxy. We will cover sub-10ms TensorRT YOLOv7 detection, ArcFace facial recognition, Jetson hardware video decoding, and a 5-day continuous and event storage retention strategy.

Building a modern, self-hosted Network Video Recorder (NVR) often forces you to make tough trade-offs. You either run an energy-hungry x86 server with a dedicated GPU pulling 150W+ 24/7, or you settle for low-power SBCs that choke when running real-time object detection across multiple high-resolution IP cameras. 

The **NVIDIA Jetson Orin Nano** (8GB) completely changes this equation. Delivering up to 40 TOPS of INT8 AI compute inside a 10W–15W power envelope, it is arguably the ultimate platform for edge surveillance. When paired with **Frigate NVR 0.18.0**, you get sub-10ms TensorRT hardware-accelerated object detection, ArcFace facial recognition, and native hardware video decoding.

However, running an NVR at home or in an office introduces a major security challenge: **How do you securely expose the web interface without compromising your network?** While Frigate has built-in authentication, wrapping the entire stack in **HAProxy** (for SSL/TLS termination) and **OAuth2-Proxy** (for Google Workspace / Gmail Single Sign-On) ensures zero-trust protection. No request touches the NVR backend without a verified Google identity and MFA.

---

## Architecture Overview

Here is how the components interact:

```
                  +-------------------------------------------------------------+
                  |                  Jetson Orin Nano (Edge)                    |
                  |                                                             |
[ Browser / ] --->| Port 8443: HAProxy (TLS Termination & Header Injection)     |
[ Tailscale ]     |    |                                                        |
                  |    v                                                        |
                  | Port 4180: OAuth2-Proxy <---> [ Google Identity Platform ]  |
                  |    |                                                        |
                  |    v (Authenticated Traffic Only)                           |
                  | Port 5000: Frigate NVR 0.18.0 Container                     |
                  |    |                                                        |
[ IP Cameras ]--->|    +---> go2rtc / FFmpeg Hardware Video Decoder (NvMMLite)  |
   (RTSP)         |    +---> TensorRT YOLOv7 Detector (~9ms inference on GPU)   |
                  |    +---> ArcFace Face Recognition (CUDA / ONNX Runtime)     |
                  |    +---> NVMe SSD Storage (Continuous & Event Recordings)   |
                  +-------------------------------------------------------------+
```

1. **HAProxy**: Listens on port `8443`, terminates HTTPS using custom SSL certificates, forwards proxy headers, and routes incoming traffic.
2. **OAuth2-Proxy**: Intercepts all traffic. Unauthenticated users are redirected to Google for SSO login. Once authenticated, session cookies validate subsequent requests, and traffic is forwarded to Frigate.
3. **Frigate 0.18.0**: Runs as a privileged Docker container leveraging the NVIDIA Container Runtime (`jetson-jp6` build) for full access to the Orin GPU and hardware multimedia engines.

---

## Hardware & Storage Sizing

### 1. Jetson Power Configuration
To extract maximum performance from the Jetson Orin Nano, ensure it operates in its unrestricted 15W mode:

```sh
# Set 15W power budget
sudo nvpmodel -m 0

# Lock clocks to maximum frequencies (optional, for lowest latency)
sudo jetson_clocks
```

### 2. NVMe Storage Calculation for a 5-Day Retention Policy
One common question when setting up an NVR is: *Will my SSD be sufficient for my retention targets?*

Suppose we have an 8-camera setup where:
- **Cameras 1–5 (Driveway, Back Yard, Porch):** Record **only on human detection** (events).
- **Cameras 6–8 (Front Gate, Main Hall, Entrance):** Require **continuous 24/7 recording**.

Let us calculate the required capacity for a **5-day retention window**:

| Stream Type | Resolution & Bitrate | Active Time / Day | 5-Day Data Volume |
| :--- | :--- | :--- | :--- |
| **Continuous (3 Cams)** | 1080p @ 3.0 Mbps | 24 Hours | ~405 GB |
| **Detection Events (5 Cams)** | 1080p @ 3.0 Mbps | ~3 Hours / Day (~12.5% motion) | ~85 GB |
| **Database & Metadata** | SQLite DB, Cache, Snapshots | Continuous | ~20 GB |
| **Total Required** | | | **~510 GB** |

A **1 TB NVMe M.2 SSD** provides ample headroom for 5 full days of mixed continuous and event recording, avoiding drive exhaustion while extending flash endurance.

---

## Step 1: Setting Up Google OAuth 2.0 Credentials

Before writing any configuration files, we need to create our OAuth client credentials on Google Cloud Console:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and create or select a project.
2. Navigate to **APIs & Services** > **OAuth consent screen**:
   - Choose **Internal** (if using Google Workspace) or **External**.
   - Fill in the required app details (e.g., App name: `Jetson NVR`).
3. Navigate to **APIs & Services** > **Credentials**:
   - Click **Create Credentials** > **OAuth client ID**.
   - Application type: **Web application**.
   - Name: `Frigate NVR Proxy`.
   - **Authorized JavaScript origins**:
     ```
     https://nvr.your-domain.com:8443
     ```
   - **Authorized redirect URIs**:
     ```
     https://nvr.your-domain.com:8443/oauth2/callback
     ```
4. Save your **Client ID** and **Client Secret**.
5. Generate a random 32-byte secret for encrypting OAuth session cookies:
   ```sh
   python3 -c 'import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())'
   ```

---

## Step 2: Configuring OAuth2-Proxy

Create a configuration file at `./configs/oauth2-proxy.cfg`:

```ini
provider = "google"
client_id = "<YOUR_GOOGLE_CLIENT_ID>.apps.googleusercontent.com"
client_secret = "<YOUR_GOOGLE_CLIENT_SECRET>"
redirect_url = "https://nvr.your-domain.com:8443/oauth2/callback"

# Restrict login to authorized email domains or specific accounts
email_domains = ["yourcompany.com", "example.com"]

cookie_secret = "<YOUR_GENERATED_32_BYTE_SECRET>"
cookie_secure = true
cookie_domains = "nvr.your-domain.com:8443"

# Upstream Frigate service running in Docker network
upstreams = ["http://frigate:5000"]
http_address = ":4180"

# Header forwarding for clean downstream proxying
pass_authorization_header = true
pass_access_token = true
pass_user_headers = true
set_authorization_header = true
skip_provider_button = true
```

### Key Options Explained:
- `provider = "google"`: Directs OAuth2-Proxy to use Google's OpenID Connect discovery endpoints.
- `email_domains`: Restricts authentication exclusively to users belonging to specified domains. Unauthorized Google accounts are rejected immediately.
- `cookie_secure = true`: Enforces the transmission of session cookies strictly over HTTPS.
- `skip_provider_button = true`: Skips the intermediate "Sign in with Google" landing page and takes the user directly to the Google login screen.
- `upstreams = ["http://frigate:5000"]`: Once authenticated, traffic flows directly to the internal Frigate container port.

> **Note:** If your organization uses Auth0 instead of Google for identity management, see my earlier guide on [Securing a Flask Application with Auth0, OAuth2-Proxy, and HAProxy](/devops/auth0/oauth2/oauth2-proxy/2025/03/08/securing-flask-application-with-auth0.html) for the equivalent OIDC setup.

---

## Step 3: Configuring HAProxy

Create the reverse proxy configuration at `./configs/haproxy.cfg`:

```cfg
global
    log /dev/log local0
    log /dev/log local1 notice
    daemon

defaults
    log global
    mode http
    option httplog
    option dontlognull
    timeout connect 5000
    timeout client  50000
    timeout server  50000

frontend https-frontend
    bind 0.0.0.0:8443 ssl crt /etc/haproxy/certs/nvr.pem
    http-request set-header X-Forwarded-Proto https
    http-request set-header X-Forwarded-Host %[req.hdr(Host)]
    http-request set-header X-Forwarded-For %[src]

    # ACL for OAuth callback and authentication endpoints
    acl oauth_path path_beg /oauth2

    # Direct all OAuth callback traffic and unauthenticated requests to oauth2-proxy
    use_backend oauth2-backend if oauth_path
    default_backend oauth2-backend

backend oauth2-backend
    server oauth2-proxy oauth2-proxy:4180 check

backend frigate-backend
    server frigate frigate:5000 check
```

### Why Route Everything Through `oauth2-backend`?
OAuth2-Proxy acts as a forward-auth proxy. When `default_backend` points to `oauth2-backend`, unauthenticated requests trigger an OAuth flow. Once the session cookie is valid, OAuth2-Proxy transparently proxies the HTTP and WebSocket connections to Frigate's backend on `frigate:5000`.

---

## Step 4: Docker Compose Setup (`compose.yaml`)

On JetPack 6, Frigate publishes dedicated container images compiled with TensorRT and CUDA support. Here is the consolidated `compose.yaml`:

```yaml
services:
  oauth2-proxy:
    image: quay.io/oauth2-proxy/oauth2-proxy:latest
    container_name: oauth2-proxy
    restart: unless-stopped
    volumes:
      - ./configs/oauth2-proxy.cfg:/etc/oauth2-proxy.cfg
    command:
      - "--config=/etc/oauth2-proxy.cfg"
      - "--insecure-oidc-allow-unverified-email=true"
      - "--skip-provider-button=true"
    ports:
      - "4180:4180"
    networks:
      - frigate-net

  haproxy:
    image: haproxy:2.8
    container_name: haproxy
    volumes:
      - ./configs/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro
      - ./certs:/etc/haproxy/certs:ro
    ports:
      - "8443:8443"
    networks:
      - frigate-net
    restart: unless-stopped
    depends_on:
      - frigate
      - oauth2-proxy

  frigate:
    container_name: frigate
    privileged: true
    restart: unless-stopped
    stop_grace_period: 30s
    image: ghcr.io/blakeblackshear/frigate:0.18.0-tensorrt-jp6
    entrypoint: ["/init"]
    shm_size: "1024mb"
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /ssd/data/frigate/config:/config
      - /ssd/data/frigate/media:/media/frigate
      - /ssd/data/frigate/models:/models
      - type: tmpfs
        target: /tmp/cache
        tmpfs:
          size: 1000000000 # 1GB RAM cache for segment processing
    ports:
      - "5000:5000"      # Internal Web UI / API
      - "8554:8554"      # RTSP feeds
      - "8555:8555/tcp"  # WebRTC
      - "8555:8555/udp"  # WebRTC
    networks:
      - frigate-net
    environment:
      FRIGATE_RTSP_PASSWORD: "<YOUR_RTSP_PASSWORD>"
      YOLO_MODELS: "yolov7-320"
      USE_FP16: "true"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

networks:
  frigate-net:
    driver: bridge
```

### Critical Tuning Parameters:
- **`shm_size: "1024mb"`**: By default, Docker allocates only 64MB of shared memory (`/dev/shm`). When running multiple 1080p or 2K camera streams, the raw uncompressed video frames shared between FFmpeg and the Python detector will rapidly overflow 64MB, leading to silent worker crashes. Allocating 1024MB provides stable headroom.
- **`tmpfs: /tmp/cache`**: Video recording segments are written to RAM first before being committed to your NVMe SSD. This drastically reduces wear and tear on your SSD NAND flash.
- **`YOLO_MODELS: "yolov7-320"` & `USE_FP16: "true"`**: Instructs Frigate on its initial run to automatically compile the YOLOv7-320 ONNX model into a TensorRT FP16 engine tailored specifically for the Orin Ampere GPU.

---

## Step 5: Frigate 0.18.0 Configuration (`config.yaml`)

Now let us configure Frigate's detectors, hardware decoding, face recognition, and recording retention policies in `/ssd/data/frigate/config/config.yaml`:

```yaml
version: 0.18-0

detectors:
  tensorrt:
    type: tensorrt
    device: 0

model:
  path: /models/yolov7-320.trt
  input_tensor: nchw
  input_pixel_format: rgb
  width: 320
  height: 320

# Optional: Enable Face Recognition using ArcFace on GPU
face_recognition:
  enabled: true
  device: GPU # Uses CUDA execution provider via ONNX Runtime

# Global recording defaults
record:
  enabled: true
  retain:
    days: 5
    mode: motion

# Global snapshots (WebP by default in 0.18 for optimal compression)
snapshots:
  enabled: true
  retain:
    default: 5

go2rtc:
  streams:
    cam_driveway:
      - rtsp://admin:<YOUR_RTSP_PASSWORD>@192.168.1.101:554/Streaming/Channels/101
    cam_front_gate:
      - rtsp://admin:<YOUR_RTSP_PASSWORD>@192.168.1.102:554/Streaming/Channels/101

cameras:
  # Camera with Person-Detection Recording (5-day retention)
  cam_driveway:
    ffmpeg:
      hwaccel_args: preset-jetson-h264
      inputs:
        - path: rtsp://127.0.0.1:8554/cam_driveway
          roles:
            - record
            - detect
    detect:
      width: 1920
      height: 1080
      fps: 5
    record:
      events:
        retain:
          default: 5
          mode: active_objects
        objects:
          - person
          - car

  # Camera with 24/7 Continuous Recording (5-day retention)
  cam_front_gate:
    ffmpeg:
      hwaccel_args: preset-jetson-h264
      inputs:
        - path: rtsp://127.0.0.1:8554/cam_front_gate
          roles:
            - record
            - detect
    detect:
      width: 1920
      height: 1080
      fps: 5
    record:
      retain:
        days: 5
        mode: all # Continuous 24/7 recording
```

### Hardware Video Decoding: Jetson Presets vs. CPU Fallback
Frigate supports `preset-jetson-h264` and `preset-jetson-h265`, which tap into Jetson's hardware NvMMLite decoders.

> **Tip from the Field:** For standard 16:9 streams (1080p, 2K, 4K), `preset-jetson-h264` works smoothly. However, if you have legacy or auxiliary cameras streaming at non-standard resolutions (such as 1024x768 4:3 at low framerates like 6 FPS), hardware decoders can sometimes experience frame negotiation stalls. In those specific cases, leaving `hwaccel_args` empty and letting the Orin CPU decode the low-bitrate stream consumes less than 3% CPU per core while providing rock-solid stability.

---

## Step 6: Deploying the Stack & Verifying Performance

### 1. Launching Services
Start the entire stack using Docker Compose:

```sh
docker compose up -d
```

### 2. The First Boot: TensorRT Compilation
During the very first launch, the Frigate container detects that `yolov7-320.trt` does not yet exist and initiates TensorRT compilation from the base ONNX weights. 

On the Jetson Orin Nano, this compilation process takes approximately **3 to 4 minutes**. You can monitor the progress with:

```sh
docker logs -f frigate
```

Once you see:
```text
[INFO] TensorRT engine compiled successfully: /models/yolov7-320.trt
[INFO] Detector tensorrt started.
```
Your detector is active and running!

### 3. Inference Latency Benchmarks
Once operational, checking the Frigate System Metrics page reveals remarkable performance:

- **Detection Model:** YOLOv7 (320x320, FP16)
- **Inference Speed:** **~9.2 ms** per frame
- **Jetson Power Draw:** **~11W–13W** total system consumption across 8 active camera feeds
- **GPU Utilization:** ~22%

Compared to a typical Google Coral TPU (which clocks around 12–15ms on MobileNet-SSD), the Orin GPU runs a significantly larger, more accurate YOLOv7 model with lower latency.

---

## Step 7: Testing the Google OAuth Flow

1. Open your browser and navigate to:
   ```
   https://nvr.your-domain.com:8443
   ```
2. You will be immediately redirected to Google's standard login interface:
   ```
   https://accounts.google.com/o/oauth2/auth?...
   ```
3. Authenticate with an email belonging to your configured `email_domains` (e.g., `user@yourcompany.com`).
4. Once verified, Google redirects you back to `https://nvr.your-domain.com:8443/oauth2/callback`.
5. OAuth2-Proxy sets a secure session cookie (`_oauth2_proxy`) and loads the Frigate 0.18 dashboard.

Any attempt to log in using an unauthorized email will result in an immediate `403 Forbidden` from OAuth2-Proxy before reaching Frigate.

---

## Exploring Frigate 0.18.0 New Features

Upgrading to **Frigate 0.18.0** brings several substantial quality-of-life enhancements:

1. **In-UI Configuration Editor:** You no longer need to SSH into your Jetson to tweak camera thresholds, motion masks, or zones. Version 0.18 features built-in config validation and live reloading directly within the web dashboard.
2. **Built-in Face Recognition (Face Library):** With ArcFace running on the Orin GPU, Frigate can detect faces in camera streams. Under the **Faces** tab, you can assign names to detected faces, train new identities, and trigger alerts when familiar or unfamiliar individuals are spotted.
3. **Optimized WebP Snapshots:** Frigate 0.18 defaults to WebP format for event snapshots, saving over 40% disk space compared to traditional JPEGs without compromising visual clarity.

---

## Conclusion

By deploying Frigate 0.18.0 on the NVIDIA Jetson Orin Nano, you get an ultra-efficient, sub-15W edge AI surveillance hub capable of running sophisticated YOLOv7 object detection and facial recognition in real time. Placing HAProxy and OAuth2-Proxy at the perimeter ensures that your private video streams remain guarded behind Google SSO and multi-factor authentication.

Now sit back, monitor your cameras with sub-10ms AI latency, and enjoy your self-hosted, enterprise-secured NVR! 🛡️📹
