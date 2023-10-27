---
layout: post
title:  "An Ansible Refresher"
date:   2023-10-19 14:10:00 +0530
categories: devops ansible
tags: devops ansible
---

## Introduction
Introducing an Ansible Refresher, designed for those keen on revisiting their Ansible expertise. In this concise program, we'll explore Ansible to set up Nginx on a Raspberry Pi. While we won't delve into exhaustive specifics, you'll gain a practical understanding of essential Ansible concepts. Furthermore, we'll furnish you with pointers to comprehensive documentation for each topic we cover, offering you the resources for deeper exploration. Let's dive right into this Ansible Refresher.

### Exploring the Essentials:
#### 1. Inventory:

Inventory is where it all begins in Ansible. We'll discover how to define hosts, groups, and variables to set the stage for our Nginx installation.

#### 2. Playbooks:

Playbooks are the scripts of Ansible, guiding the automation process. We'll learn how to create a playbook to orchestrate our Nginx installation.

#### 3. Facts:

Facts provide valuable information about target hosts. We'll explore how to gather and use facts in our playbook.

#### 4. Roles:

Roles are Ansible's way of organizing and reusing tasks. We'll create roles for our Nginx installation to keep our playbook clean and maintainable.

#### 5. Tags:

Tags allow us to selectively run tasks. We'll see how to tag tasks in our playbook to control execution.

#### 6. Secrets:

Managing sensitive information is crucial. We'll discuss best practices for handling secrets and credentials in Ansible.

#### 7. Jinja Templates:

Templating with Jinja allows us to create dynamic configurations. We'll use Jinja templates to customize Nginx configurations.

#### 8. Handlers:

Handlers respond to specific events and are often used to restart services. We'll configure handlers to restart Nginx when necessary.

By the end of this refresher, you'll have hands-on experience with these fundamental Ansible concepts. Plus, with the provided documentation, you'll be well-equipped to explore these topics in more depth on your own. Let's begin our Ansible journey by installing Nginx on your Raspberry Pi!

## Inventory
The default path of Ansible Inventory is /etc/ansible/hosts. But we are going to use a custom location and use an inventory file per host in this case. Two examples of the same inventory are as follows:

#### INI Format:

```
pi4 ansible_host=pi4.seneshore.com ansible_ssh_host=192.168.1.15 ansible_ssh_user=ubuntu
```

#### YAML Format:

```
---
raspberry:
  hosts:
    pi4:
      ansible_host: pi4.seneshore.com
      ansible_ssh_host: 192.168.1.15
      ansible_ssh_user: ubuntu
```

The location of the non-default inventory file can be specified in ansible.cfg or use the -i option in CLI with ansible-playbook.

Ref: [How to build your inventory](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html)

## Role
Let's start with our role next. We'll name the role nginx_pi4. First, create a directory structure as below:

```playbooks/
└── roles
    └── nginx_pi4
        ├── defaults
        ├── handlers
        ├── tasks
        └── templates
```
Next, we'll create the main task `playbooks/roles/nginx_pi4/tasks/main.yml` as below:

<script src="https://gist.github.com/prakritish/90992df3fb59181c93b8bab49b5863cc.js"></script>

The first instruction in this file uses Ansibles inbuilt module [ansible.builtin.apt](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/apt_module.html) to install `nginx`. We also added options to run `apt-get` prior to installation and also clean up the cache, remove packages which are no longer required, etc.

We are also using [tags](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_tags.html) for the tasks. We'll touch upon tags later in the article.

The second and third instructions are to import and execute the instructions from other task files `self-signed-cert.yml` and `generate-config.yml` respectively from the same role.

In the third instruction (Line 22), we also have the [notify](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_handlers.html#notifying-handlers) directive which instructs that if the corresponding instruction is successfully executed, the handler named "Restart Nginx" should be called.  The handler is also part of the role and should be placed at `playbooks/roles/nginx_pi4/handlers/main.yml`.
```
- name: Restart Nginx
  service:
    name: nginx
    state: restarted
```


`playbooks/roles/nginx_pi4/tasks/self-signed-cert.yml`
<script src="https://gist.github.com/prakritish/3975f487286b716dc2c3bd35e0a446fd.js"></script>
In this task file, we are:

- Generating Private Key - [community.crypto.openssl_privatekey](https://docs.ansible.com/ansible/latest/collections/community/crypto/openssl_privatekey_module.html)
- Generating certificate signing request (CSR) for self-signed certificate - [community.crypto.openssl_csr_pipe](https://docs.ansible.com/ansible/latest/collections/community/crypto/openssl_csr_pipe_module.html)
- Generating Self Signed Certificate - [community.crypto.x509_certificate](https://docs.ansible.com/ansible/latest/collections/community/crypto/x509_certificate_module.html)
- Generating DH Parameters - [community.crypto.openssl_dhparam](https://docs.ansible.com/ansible/latest/collections/community/crypto/openssl_dhparam_module.html)
- Finally uploading a file which contains the password for the Generated Private Key - [ansible.builtin.copy](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/copy_module.html)


We are also using a few variables in this task. A few of the variables are defined in `playbooks/roles/nginx_pi4/defaults/main.yml`.

<script src="https://gist.github.com/prakritish/80658724d5d231a55458a30aa251ede2.js"></script>

The other variables ansible_host come from inventory and the variable csr is created within the task file by the register directive in the second instruction i.e., to generate CSR for self-signed certificate. 


The next task file `playbooks/roles/nginx_pi4/tasks/generate-config.yml` is used to create the Nginx Configuration from Jinja2 Template.

```
---
- name: Generate Nginx Configuration
  template:
    src: nginx.j2
    dest: /etc/nginx/sites-available/ssl-default

- name: Remove default config
  file:
    path: /etc/nginx/sites-enabled/default
    state: absent

- name: Create symlink for sites-enabled
  file:
    src: /etc/nginx/sites-available/ssl-default
    dest: /etc/nginx/sites-enabled/ssl-default
    state: link
```
The Jinja2 Template is also part of the role and can be found at `playbooks/roles/nginx_pi4/templates/nginx.j2`
```
server {
  listen 443 ssl;
  server_name {{ ansible_host }};

  # SSL certificate and key files
  ssl_certificate {{ ssl_cert }};
  ssl_certificate_key {{ ssl_privkey }};
  ssl_password_file {{ ssl_privkey_pass_file }};

  # SSL settings
  ssl_protocols TLSv1.2 TLSv1.3;
  ssl_ciphers 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:ECDHE-RSA-AES128-GCM-SHA256';
  ssl_prefer_server_ciphers off;
  ssl_dhparam {{ ssl_dhpharm }};
  ssl_session_timeout 1d;
  ssl_session_cache shared:SSL:50m;
  ssl_stapling on;
  ssl_stapling_verify on;
  add_header Strict-Transport-Security "max-age=63072000" always;

  # Additional SSL settings
  ssl_ecdh_curve X25519:secp384r1:prime256v1;
  ssl_session_tickets off;

  # Configure document root
  root {{ nginx_root }};

  location / {
    try_files $uri /index.html index.php;
  }
  # Add other Nginx directives as needed, such as error pages, access control, etc.
}
```

## Playbook

Finally, we need a playbook to use the created role. We'll call it nginx.yml.
<script src="https://gist.github.com/prakritish/d10c2d01c1860acd23243893437196d2.js"></script>

Line 2 - The name of the playbook

Line 3 - This is where we specify the hosts (list of hosts) where the playbook should be executed. Even though we have used all, we would restrict the deployment using conditions.

Line 4 - This is where we instruct Ansible to gather facts/details of the Hosts in the inventory.

Line 6 - This is where we start the task list.

Line 7-8 - We have only one task i.e., to use the custom role we created

Line 10-13 - This is where we specify the restrictions using the when clause to limit deployment to hosts which fulfil the given criterion.

Line 14-15 - We specify the special tag always here. This is for some reason required if we want to use the tags on the role. Unless we use this, specifying a tag from the command line has a weird effect of nothing getting executed. We'll explore this in the section below.

## Usage
Your workspace should look like something below now. I have an extra inventory file for localhost, but you may skip it.
```
├── inventory
│   ├── localhost
│   └── pi4
└── playbooks
    ├── nginx.yml
    └── roles
        └── nginx_pi4
            ├── defaults
            │   └── main.yml
            ├── handlers
            │   └── main.yml
            ├── tasks
            │   ├── generate-config.yml
            │   ├── main.yml
            │   └── self-signed-cert.yml
            └── templates
                └── nginx.j2
```
We can now run the code from our favourite terminal as below:

```
ansible-playbook -i inventory playbooks/nginx.yml
``` 
The output should be something like below:
```
ansible-playbook -i inventory playbooks/nginx.yml

PLAY [Install Nginx on Raspberry Pi4] ****************************************************************

TASK [Gathering Facts] *******************************************************************************
ok: [mbp16]
ok: [pi4]

TASK [Use nginx_pi4 role] ****************************************************************************
skipping: [mbp16]

TASK [nginx_pi4 : Install Nginx] *********************************************************************
ok: [pi4]

TASK [nginx_pi4 : Create private key (RSA, 4096 bits)] ***********************************************
ok: [pi4]

TASK [nginx_pi4 : Create certificate signing request (CSR) for self-signed certificate] **************
changed: [pi4]

TASK [nginx_pi4 : Generate Self Signed Certificate] **************************************************
ok: [pi4]

TASK [nginx_pi4 : Generate DH Parameters with a different size (2048 bits)] **************************
ok: [pi4]

TASK [nginx_pi4 : Add SSL Private Key Password File] *************************************************
ok: [pi4]

TASK [nginx_pi4 : Generate Nginx Configuration] ******************************************************
ok: [pi4]

TASK [nginx_pi4 : Remove default config] *************************************************************
ok: [pi4]

TASK [nginx_pi4 : Create symlink for sites-enabled] **************************************************
ok: [pi4]

PLAY RECAP *******************************************************************************************
mbp16                      : ok=1    changed=0    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
pi4                        : ok=10   changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

In case, you want to execute only specific a task, you may do so as below.

### Use Case - I
The playbook was successful till SSL Certificate generation, therefore you don't want to spend time by running the full playbook and want it to just generate the Neginx Configuration file and deploy it.
```
ansible-playbook -i inventory playbooks/nginx.yml --tags config

PLAY [Install Nginx on Raspberry Pi4] ****************************************************************

TASK [Gathering Facts] *******************************************************************************
ok: [mbp16]
ok: [pi4]

TASK [Use nginx_pi4 role] ****************************************************************************
skipping: [mbp16]

TASK [nginx_pi4 : Generate Nginx Configuration] ******************************************************
ok: [pi4]

TASK [nginx_pi4 : Remove default config] *************************************************************
ok: [pi4]

TASK [nginx_pi4 : Create symlink for sites-enabled] **************************************************
ok: [pi4]

PLAY RECAP *******************************************************************************************
mbp16                      : ok=1    changed=0    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
pi4                        : ok=4    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```
### Use Case - II
The playbook was only successful in installing Nginx and you would like to run all the steps except for the Nginx installation steps
```
ansible-playbook -i inventory playbooks/nginx.yml --skip-tags install
BECOME password:

PLAY [Install Nginx on Raspberry Pi4] ****************************************************************

TASK [Gathering Facts] *******************************************************************************
ok: [mbp16]
ok: [pi4]

TASK [Use nginx_pi4 role] ****************************************************************************
skipping: [mbp16]

TASK [nginx_pi4 : Create private key (RSA, 4096 bits)] ***********************************************
ok: [pi4]

TASK [nginx_pi4 : Create certificate signing request (CSR) for self-signed certificate] **************
changed: [pi4]

TASK [nginx_pi4 : Generate Self Signed Certificate] **************************************************
ok: [pi4]

TASK [nginx_pi4 : Generate DH Parameters with a different size (2048 bits)] **************************
ok: [pi4]

TASK [nginx_pi4 : Add SSL Private Key Password File] *************************************************
ok: [pi4]

TASK [nginx_pi4 : Generate Nginx Configuration] ******************************************************
ok: [pi4]

TASK [nginx_pi4 : Remove default config] *************************************************************
ok: [pi4]

TASK [nginx_pi4 : Create symlink for sites-enabled] **************************************************
ok: [pi4]

PLAY RECAP *******************************************************************************************
mbp16                      : ok=1    changed=0    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
pi4                        : ok=9    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```
