---
layout: post
title:  "Kubernetes - Cheat Sheet"
date:   2023-10-19 13:43:25 +0530
categories: devops kubernetes
tags: devops kubernetes
---
# Kubernetes Cheat Sheet
## Kubernetes Terminology
* A **cluster** is a set of nodes that run containerized applications and are managed by the master node.
* A **node** is a machine in the cluster that runs pods. Nodes can be either master or worker nodes.
* A **pod** is the smallest unit of deployment in Kubernetes. A pod consists of one or more containers that share the same network and storage.
* A **service** is an abstraction that defines a logical set of pods and a policy to access them. Services provide load balancing, service discovery, and external access to pods.
* A **deployment** is an object that defines the desired state of a pod or a set of pods. Deployments manage the creation, scaling, and updating of pods.
* A **replicaSet** is an object that ensures that a specified number of pod replicas are running at any given time. ReplicaSets are usually created and managed by deployments.
* An **ingress** is an object that defines rules for external access to services in the cluster. Ingresses use an ingress controller to route traffic according to the rules.
* A **configMap** is an object that stores configuration data as key-value pairs. ConfigMaps can be mounted as volumes or environment variables in pods.
* A **secret** is an object that stores sensitive data such as passwords, tokens, or keys. Secrets can be mounted as volumes or environment variables in pods.
* A **volume** is an object that provides persistent storage for pods. Volumes can be either local or remote, and support various types of storage backends.
* A **namespace** is an object that creates a logical isolation for resources in the cluster. Namespaces can be used to group resources by project, team, or environment.
* **PDB:** PDB stands for Pod Disruption Budget, which is a way to limit the number of voluntary disruptions that can affect a set of pods in a cluster. A PDB defines the minimum number or percentage of pods that must be available for a certain application or workload. This helps to ensure high availability and resilience for critical services.
* **HPA:** HPA stands for Horizontal Pod Autoscaler, which is a controller that automatically scales the number of pods in a deployment or replica set based on the observed CPU utilization or other custom metrics. An HPA allows you to adjust your application’s performance and resource consumption according to the changing demand.
* **Taint:** A taint is a key-value pair that is attached to a node, indicating that the node has some special property or condition that affects its scheduling. For example, you can taint a node with key=dedicated and value=database to mark it as dedicated for running database pods only.
* **Toleration:** A toleration is a key-value pair that is attached to a pod, indicating that the pod can tolerate some taints on nodes. For example, you can add a toleration with key=dedicated and value=database to a pod to allow it to be scheduled on nodes with the corresponding taint.
* **CRD:** CRD stands for Custom Resource Definition, which is a way to extend the Kubernetes API with your own custom resources. A custom resource is an object that represents some domain-specific concept or functionality in your application. For example, you can create a custom resource for a blog post, a user profile, or a shopping cart.
* **Operator:** An operator is a software extension that uses custom resources and controllers to automate complex tasks and workflows in Kubernetes. An operator acts as a domain expert that knows how to manage your application’s lifecycle, such as installation, configuration, backup, recovery, scaling, and upgrading.

## Kubernetes Networking
Kubernetes networking is based on the principle that pods can communicate with each other across nodes without NAT, and nodes can communicate with pods without NAT. This creates a flat network space where every pod has a unique IP address.

To achieve this, Kubernetes uses the following components:
* **Container Network Interface (CNI):** A standard for configuring network interfaces for containers. Kubernetes supports various CNI plugins, such as Calico, Cilium, Flannel, etc.
* **Kube-proxy:** A component that runs on each node and implements the service abstraction by forwarding traffic to the appropriate pods.
* **DNS:** A component that provides DNS resolution for services and pods in the cluster. Kubernetes uses CoreDNS as the default DNS server.
* **Ingress:** A component that provides external access to services in the cluster. Kubernetes supports various ingress controllers, such as NGINX, Traefik, Istio, etc.

## Kubernetes Security
Kubernetes security is based on the principle of least privilege, where every resource has the minimum level of access required to function. Kubernetes uses the following components to enforce security:

* **Authentication:** The process of verifying the identity of a user or a service account. Kubernetes supports various authentication methods, such as certificates, tokens, OIDC, etc.
Authorization: The process of determining whether a user or a service account is allowed to perform an action on a resource. Kubernetes supports various authorization modes, such as RBAC, ABAC, Node, Webhook, etc.
* **Admission Controllers:** The components that intercept requests to the API server and modify or reject them based on certain rules. Kubernetes supports various admission controllers, such as PodSecurityPolicy, ResourceQuota, LimitRanger, etc.
* **Encryption:** The process of protecting data from unauthorized access. Kubernetes supports encryption at rest for secrets and encryption in transit for API server communication.

# Kubernetes Monitoring
Kubernetes monitoring is essential for ensuring the reliability and performance of your cluster and applications. Kubernetes provides the following components for monitoring:
Metrics Server: A component that collects resource metrics from nodes and pods and exposes them to the API server.

* **Prometheus**: A component that scrapes and stores metrics from nodes, pods, services, and other sources. Prometheus also provides a query language and an alerting system.
* **Grafana**: A component that provides a graphical dashboard for visualizing and analyzing metrics from Prometheus and other sources.
* **Loki**: A component that collects and stores logs from nodes and pods. Loki also integrates with Grafana for log visualization and analysis.
* **Jaeger**: A component that traces and monitors the distributed transactions between microservices. Jaeger also integrates with Grafana for trace visualization and analysis.

I hope this cheat sheet helps you learn more about Kubernetes and its features. If you want to learn more, you can check out these web resources:

* **[Kubernetes Documentation](https://kubernetes.io/docs/setup/best-practices/)**: The official documentation for Kubernetes.
* **[Kubernetes Best Practices](https://cloud.google.com/blog/products/containers-kubernetes/kubernetes-best-practices-resource-requests-and-limits)**: A series of blog posts from Google Cloud on how to get the most out of your Kubernetes environment.
* **[Kubernetes Best Practices](https://spacelift.io/blog/kubernetes-best-practices)**: A list of 15 best practices for developers working with Kubernetes from Spacelift.

# Kubernetes Commands
## kubectl
kubectl is the command-line tool for interacting with the Kubernetes API server and controlling Kubernetes clusters. It allows you to create, update, delete, and inspect various resources in your cluster.
### Basic Syntax
```
kubectl [command] [type] [name] [flags]
```
* command: The operation to perform on one or more resources, such as create, get, delete, describe, etc.
* type: The type of resource to operate on, such as pod, service, deployment, etc.
name: The name of the resource to operate on, such as my-pod, my-service, etc.
* flags: Optional flags to modify the behavior of the command, such as -n for namespace, -o for output format, -f for filename, etc.

### Common Commands
```
# Create a resource from a file
kubectl create -f <file>

# Create a resource from stdin
kubectl create -f -

# Get information about a resource
kubectl get <type> <name>

# Get information about all resources
kubectl get all

# Describe a resource in detail
kubectl describe <type> <name>

# Delete a resource
kubectl delete <type> <name>

# Delete a resource from a file
kubectl delete -f <file>

# Edit a resource
kubectl edit <type> <name>

# Apply changes to a resource from a file
kubectl apply -f <file>

# Apply changes to a resource from stdin
kubectl apply -f -

# Scale a deployment
kubectl scale deployment <name> --replicas=<number>

# Expose a deployment as a service
kubectl expose deployment <name> --port=<port> --type=<type>

# Port-forward a pod to a local port
kubectl port-forward pod/<name> <local-port>:<pod-port>

# Exec a command in a pod
kubectl exec pod/<name> -- <command>

# Log into a pod
kubectl exec pod/<name> -it -- /bin/bash

# Copy files between local and pod
kubectl cp <source> <destination>

# Label a resource
kubectl label <type> <name> <key>=<value>

# Annotate a resource
kubectl annotate <type> <name> <key>=<value>
```
### Kubectl Cheat Sheet
#### Getting started
* To get the version of kubectl and the cluster, use:
```
kubectl version
```
* To get the list of nodes in the cluster, use:
```
kubectl get nodes
```
* To get the list of pods in the default namespace, use:
```
kubectl get pods
```
* To get the list of pods in a specific namespace, use:
```
kubectl get pods -n <namespace>
```
* To get the details of a specific pod, use:
```
kubectl describe pod <pod-name>
```
#### Creating and deleting resources
* To create a resource from a YAML file, use:
```
kubectl create -f <file-name>.yaml
```
* To delete a resource by name, use:
```
kubectl delete <resource-type> <resource-name>
```
* To delete a resource by label, use:
```
kubectl delete <resource-type> -l <label-key>=<label-value>
```
* To delete all resources in a namespace, use:
```
kubectl delete all --all -n <namespace>
```
#### Updating and scaling resources
* To update a resource from a YAML file, use:
```
kubectl apply -f <file-name>.yaml
```
* To edit a resource interactively, use:
```
kubectl edit <resource-type> <resource-name>
```
* To scale a deployment or a replica set, use:
```
kubectl scale <resource-type> <resource-name> --replicas=<number>
```
#### Debugging and troubleshooting
* To get the logs of a pod, use:
```
kubectl logs <pod-name>
```
* To get the logs of a specific container in a pod, use:
```
kubectl logs <pod-name> -c <container-name>
```
* To execute a command in a container, use:
```
kubectl exec -it <pod-name> -c <container-name> -- <command>
```
* To port-forward a pod to a local port, use:
```
kubectl port-forward <pod-name> <local-port>:<pod-port>
```
#### Configuring and managing contexts
* To get the current context, use:
```
kubectl config current-context
```
* To get the list of contexts, use:
```
kubectl config get-contexts
```
* To switch to a different context, use:
```
kubectl config use-context <context-name>
```
* To create a new context, use:
```
kubectl config set-context <context-name> --cluster=<cluster-name> --user=<user-name> --namespace=<namespace>
```
## Helm Cheat Sheet
Helm is a package manager for Kubernetes that allows you to deploy applications using charts, which are collections of YAML files that describe the resources needed by the application.

### Basic Helm Concepts
**Chart:** A package of YAML files that define the application and its dependencies.
**Repository:** A collection of charts that can be accessed by a name and a URL.
**Release:** An instance of a chart deployed in a Kubernetes cluster.
**Revision:** A version of a release that can be rolled back to.

### Common Helm Commands
#### Chart Management
* Create a new chart with the given name
```
helm create <name>
```
* Package a chart into a compressed archive file.
```
helm package <chart>
```
* Check a chart for possible issues and errors.
```
helm lint <chart>
```
* Show all the information about a chart, including values, readme, and dependencies.
```
helm show all <chart>
```
* Show the default values of a chart.
```
helm show values <chart>
```
* Download a chart from a repository to the local cache.
```
helm pull <chart>
```
* List the dependencies of a chart.
```
helm dependency list <chart>
```
* Update the dependencies of a chart by downloading them from their sources.
```
helm dependency update <chart>
```

#### Install and Uninstall Apps
* Install a chart with the given name in the default namespace.
```
helm install <name> <chart>
```
* Install a chart with the given name in the specified namespace.
```
helm install <name> <chart> --namespace <namespace>
```
* Install a chart with the given name and override some values on the command line.
```
helm install <name> <chart> --set key1=val1,key2=val2
```
* Install a chart with the given name and override some values from a file or a URL.
```
helm install <name> <chart> --values <file>
```
* Test an installation without actually deploying anything and show the output.
```
helm install <name> <chart> --dry-run --debug
```
* Verify the integrity of a chart before installing it.
```
helm install <name> <chart> --verify
```
* Uninstall a release with the given name.
```
helm uninstall <name>
```

#### Perform App Upgrade and Rollback
* Upgrade a release to a new version of a chart.
```
helm upgrade <release> <chart>
```
* Upgrade a release and roll back if the upgrade fails.
```
helm upgrade <release> <chart> --atomic
```
* Upgrade a release or install it if it does not exist.
```
helm upgrade <release> <chart> --install
```
* Upgrade a release to a specific version of a chart.
```
helm upgrade <release> <chart> --version <version>
```
* Upgrade a release and override some values from a file or a URL.
```
helm upgrade <release> <chart> --values <file>
```
* Upgrade a release and override some values on the command line.
```
helm upgrade <release> <chart> --set key1=val1,key2=val2
```
* Upgrade a release by recreating the resources if necessary.
```
helm upgrade <release> <chart> --force
```
* Roll back a release to a previous revision.
```
helm rollback <release> <revision>
```
* Roll back a release and delete any new resources created during the rollback if it fails.
```
helm rollback <release> <revision> --cleanup-on-fail
```

#### List, Add, Remove, and Update Repositories
* List all the repositories added to Helm.
```
helm repo list
```
* Add a new repository with the given name and URL.
```
helm repo add <name> <url>
```
* Remove an existing repository with the given name.
```
helm repo remove <name>
```
* Update the local cache of charts from all the repositories.
```
helm repo update
```

#### Helm Release Monitoring
* List all the releases in the default namespace.
```
helm list
```
* List all the releases in all namespaces.
```
helm list --all-namespaces
```
* List all the releases, including deleted ones, in the default namespace.
```
helm list --all
```
* Show the status of a release, including deployed resources and notes.
```
helm status <release>
```
* Show the revision history of a release.
```
helm history <release>
```