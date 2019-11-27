# Kubernetes Installation Guide

This tutorial will install the kubernetes 1.15.1 with the following environments.
- Environments
    - Docker 19.03
    - Ubuntu 18.04

## Pre-install some essentials

```sh=
# Add source
sudo apt-get install apt-transport-https curl -y
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-add-repository "deb http://apt.kubernetes.io/ kubernetes-xenial main"
sudo apt-get update
```

## Install k8s main program

```sh
sudo apt-get install kubelet kubeadm kubectl -y
sudo swapoff -a
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
```

## Make kubectl connect to kubeadm

```sh
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

## Install k8s network

```sh
sudo kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/62e44c867a2846fefb68bd5f178daf4da3095ccb/Documentation/kube-flannel.yml
```

## Check if k8s installation finished or not

```sh
# check whether master is ready
kubectl get node

# check whether network is ready
kubectl -n kube-system get pod    

# Print Join-Command ( for client node )
kubeadm token create --print-join-command

# Enable deployment on master
kubectl taint nodes --all node-role.kubernetes.io/master-
```

## Trouble Shooting

### Your pod can't connect to Internet

Execute `kubeadm -n kube-system get pod` to check network.
If `kube-flannel` is crashingOff, the reason is that you execute `sudo kubeadm init` instead of `sudo kubeadm init --pod-network-cidr=10.244.0.0/16`. You need to assign pod network cidr.

You have two way
---
1. Update kubeadm config
2. Reset kubeadm

#### how to update kubeadm config

1. Generate [config.yaml](#config.yaml)
2. Upgrade kubeadm setting
```
sudo kubeadm upgrade apply --config config.yaml
```
3. Restart `kube-flannel` pod
```
kubectl -n kube-system delete kube-flannel-ds-amd64-l49js
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/62e44c867a2846fefb68bd5f178daf4da3095ccb/Documentation/kube-flannel.yml
```

### "cni0" already has an IP address different from 10.244.2.1/24

```
sudo su -
rm -rf /var/lib/cni/flannel/* && rm -rf /var/lib/cni/networks/cbr0/* && ip link delete cni0  
rm -rf /var/lib/cni/networks/cni0/*
kubeadm reset
kubeadm join (~~~)
```
[Links](https://www.cnblogs.com/jiuchongxiao/p/8942080.html)

### Node not ready
```
journalctl -f -u kubelet
```




#### config.yaml
```
apiServer:
  extraArgs:
    authorization-mode: Node,RBAC
  timeoutForControlPlane: 4m0s
apiVersion: kubeadm.k8s.io/v1beta2
certificatesDir: /etc/kubernetes/pki
clusterName: kubernetes
controllerManager: {}
dns:
  type: CoreDNS
etcd:
  local:
    dataDir: /var/lib/etcd
imageRepository: k8s.gcr.io
kind: ClusterConfiguration
kubernetesVersion: v1.15.3
networking:
  dnsDomain: cluster.local
  podSubnet: 10.244.0.0/16
  serviceSubnet: 10.96.0.0/12
scheduler: {}
```







## Cheat sheet
```sh
kubeadm config view    # View the config in kubeadm
kubeadm -n kube-system get pod    # View pods under namespaces and check
kubectl --namespace kube-system logs -f kube-flannel-ds-amd64-l49js

```

[kubeadm config file ref](https://github.com/kubernetes/kubeadm/issues/1464)

[How to reset kubeadm](https://ithelp.ithome.com.tw/articles/10209632)

[kubeadm install](https://tachingchen.com/tw/blog/kubernetes-installation-with-kubeadm/)

[kubeadm install 2](https://ithelp.ithome.com.tw/articles/1020911)



## How to Reset K8s

```sh
sudo kubeadm reset
sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -X
```


## How to label nodes

```bash
kubectl get nodes --show-labels
kubectl label node/analytics role=cpu
```




