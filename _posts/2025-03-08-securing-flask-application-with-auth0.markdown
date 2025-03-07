---
layout: post
title:  Securing a Flask Application with Auth0, OAuth2-Proxy, and HAProxy"
date:   2025-03-08 01:00:00 +0530
categories: devops auth0 OAuth2 OAuth2-Proxy
tags: devops auth0 OAuth2 OAuth2-Proxy
---

## Introduction
In this guide, we will set up authentication for a Flask application using Auth0 and OAuth2-Proxy. The application and OAuth2-Proxy run as Docker containers, while HAProxy is configured directly on the host system to manage authentication and routing.

## Prerequisites
Before starting, ensure you have:

- A Flask application running in a Docker container.
- OAuth2-Proxy configured to authenticate users via Auth0.
- HAProxy set up as a reverse proxy to enforce authentication.

## Docker Compose Configuration
We use Docker Compose to define and manage our Flask application and OAuth2-Proxy.

### `compose.yaml`
```yaml
services:
  operator:
    build:
      context: model_studio/
      dockerfile: Dockerfile
    restart: unless-stopped
    volumes:
      - ./model_studio/.secret:/secrets/recommend_demo 
    network_mode: "host"

  oauth2-proxy:
    image: quay.io/oauth2-proxy/oauth2-proxy:latest
    restart: unless-stopped
    volumes:
      - ~/oauth2-proxy/oauth2-proxy.cfg:/etc/oauth2-proxy.cfg
    network_mode: "host"
    command: 
      - "--config=/etc/oauth2-proxy.cfg"
      - "--insecure-oidc-allow-unverified-email=true"
      - "--skip-provider-button=true"
```

### Explanation of Docker Compose Options

- **`operator`** service:

  - `build.context`: Specifies the directory where the Dockerfile for the Flask application is located.
  - `restart: unless-stopped`: Ensures the container restarts unless manually stopped.
  - `volumes`: Mounts a secret directory for storing credentials.
  - `network_mode: host`: Uses the host network to allow direct communication with HAProxy and OAuth2-Proxy.

- **`oauth2-proxy`** service:

  - `image`: Uses the latest OAuth2-Proxy image from Quay.
  - `restart: unless-stopped`: Ensures the proxy restarts unless manually stopped.
  - `volumes`: Mounts the OAuth2-Proxy configuration file.
  - `command`: Specifies additional options to modify OAuth2-Proxy behavior.
  - `network_mode: host`: Ensures that OAuth2-Proxy can bind to port 4180 and communicate with HAProxy directly.

### Explanation of `command` options:

- `--config=/etc/oauth2-proxy.cfg`: Specifies the configuration file for OAuth2-Proxy.
- `--insecure-oidc-allow-unverified-email=true`: Allows users with unverified emails to authenticate (use with caution in production; unless you enjoy living on the edge of security).
- `--skip-provider-button=true`: Bypasses the provider selection button for a seamless login experience because, let’s be honest, no one likes extra clicks.

## Configuring OAuth2-Proxy

OAuth2-Proxy handles authentication by redirecting users to Auth0 and verifying their credentials.

### `oauth2-proxy.cfg`

```ini
provider = "oidc"
client_id = "<AUTH0_CLIENT_ID>"
client_secret = "<AUTH0_CLIENT_SECRET>"
redirect_url = "https://model-studio.seneshore.com/oauth2/callback"
oidc_issuer_url = "https://your-auth0-domain/"
email_domains = "seneshore.com"
cookie_secret = "<RANDOM_COOKIE_SECRET>"
cookie_secure = true
cookie_domains = "model-studio.seneshore.com"
upstreams = ["http://127.0.0.1:7860/"]
http_address = "0.0.0.0:4180"
pass_authorization_header = true
pass_access_token = true
pass_user_headers = true
set_authorization_header = true
skip_provider_button = true
```

Replace `<AUTH0_CLIENT_ID>`, `<AUTH0_CLIENT_SECRET>`, and `<RANDOM_COOKIE_SECRET>` with your actual Auth0 credentials.

### Explanation of OAuth2-Proxy Configuration Options

- `provider = "oidc"`: Specifies that we are using OpenID Connect (OIDC) for authentication.
- `client_id` and `client_secret`: Provided by Auth0 to authenticate OAuth2-Proxy.
- `redirect_url`: The callback URL registered in Auth0.
- `oidc_issuer_url`: The Auth0 domain that issues authentication tokens.
- `email_domains`: Restricts access to users with a specific email domain.
- `cookie_secret`: A random secret used to encrypt cookies.
- `cookie_secure = true`: Ensures cookies are only transmitted over HTTPS (because security matters!).
- `upstreams`: The backend service OAuth2-Proxy will forward authenticated traffic to.
- `http_address = "0.0.0.0:4180"`: Configures OAuth2-Proxy to listen on port 4180.
- `pass_authorization_header`, `pass_access_token`, `pass_user_headers`: Pass authentication details to the upstream service.
- `set_authorization_header = true`: Ensures the Authorization header is set in requests.
- `skip_provider_button = true`: Bypasses the provider selection page for a seamless login experience.

## Configuring HAProxy

HAProxy ensures that only authenticated users can access the Flask application.

### `/etc/haproxy/haproxy.cfg`

```cfg
global
    log /dev/log local0
    log /dev/log local1 notice
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin expose-fd listeners
    stats timeout 30s
    user haproxy
    group haproxy
    daemon

defaults
    log global
    mode http
    option httplog
    option dontlognull
    timeout connect 5000
    timeout client  50000
    timeout server  50000

frontend http-frontend
    bind *:80
    redirect scheme https code 301 if !{ ssl_fc }

frontend https-frontend
    bind *:443 ssl crt /etc/haproxy/certs/model-studio.seneshore.com.pem
    http-request set-header X-Forwarded-Proto https
    http-request set-header X-Forwarded-Host %[req.hdr(Host)]
    http-request set-header X-Forwarded-For %[src]
    
    acl oauth_path path_beg /oauth2
    use_backend oauth2-backend if oauth_path
    default_backend oauth2-backend

backend oauth2-backend
    server oauth2-proxy 127.0.0.1:4180 check

backend app-backend
    server app 127.0.0.1:7860 check
```

## Running the Setup

1. **Start the Docker containers**:
   ```sh
   docker compose up -d
   ```
2. **Restart HAProxy** to apply the configuration:
   ```sh
   systemctl restart haproxy
   ```

## Testing the Authentication Flow

1. Open your browser and navigate to `https://model-studio.seneshore.com`.
2. You will be redirected to the Auth0 login page.
3. After successful authentication, you will be redirected back to the Flask application.

## Conclusion

By integrating Auth0, OAuth2-Proxy, and HAProxy, we have successfully enabled secure authentication for a Flask application. This setup ensures that only authorized users can access the application while leveraging the flexibility of OAuth2-Proxy and HAProxy. Now sit back, relax, and enjoy your well-secured app! 🔐😎

