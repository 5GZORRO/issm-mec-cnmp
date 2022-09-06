# Reset Kubernetes Cluster
Follow the below instructions in this order, to reset a kubernetes cluster. The instructions assume you already have a k8s cluster installed via [these instructions](./kubernetes.md)

## Reset master

Log into the master

### Reset control plane

Become sudo: `sudo -s`

```
kubeadm reset
```

**after reset, it's recommended to reboot the node to reset the stale cni subnets **

### Turn swap off

```
sudo swapoff -a
```

Run `sudo vi /etc/fstab` and comment out swap partition

Invoke `top` and ensure swap not used

### Re-install

```
kubeadm init --pod-network-cidr=10.244.0.0/16
sysctl net.bridge.bridge-nf-call-iptables=1
```

Exit `sudo`

```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

Install flannel as default CNI. The below taken from [here](https://github.com/coreos/flannel/blob/master/README.md#deploying-flannel-manually)

```bash
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```

Wait until all running

```
kubectl get pod --all-namespaces
```

## Reset nodes

Log into to node

Become sudo: `sudo -s`

```
kubeadm reset
```

**after reset, it's recommended to reboot the node to reset the stale cni subnets **

### Turn swap off

```
sudo swapoff -a
```

Run `sudo vi /etc/fstab` and comment out swap partition

Invoke `top` and ensure swap not used

### Re-join

```
sysctl net.bridge.bridge-nf-call-iptables=1
```

```
kubeadm join ....
```

Repeat above for every node
