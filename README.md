# issm-mec-cnmp

Use [these instructions](docs/kubernetes.md) to deploy three kubernetes clusters

* OCM Hub: 1 master, 1 worker
* Core: 1 master, 2 workers
* Edge: 1 master, 1 worker

Create two fresh **Ubuntu 20.04** VMs: 4 vCPU, 8 GB RAM, 50 GB for

* gNB node
* UE (user-equipment)

**Important**: ensure VMs network interfaces set with the same name e.g. `ens3`

![Testbed](images/multi-cluster-zorro-1.png)

## Open Cluster Manager

After creating the three kubernetes clusters, install OCM and register it with the two clusters 'Core' and 'Edge'

Follow [these](./docs/ocm.md) instructions to install OCM

**Note:** register the Core and Edge clusters `bcn-core` and `bcn-edge` respectively

## K8s networking

Perform the below instructions to install multus and IPAM whereabouts

Do this for both core and edge clusters

### Multus

Log into k8s master

Perform the below steps per this [Installation](https://github.com/k8snetworkplumbingwg/multus-cni/blob/v3.8/docs/quickstart.md#installation) guide

```
cd ~
git clone https://github.com/k8snetworkplumbingwg/multus-cni.git && cd multus-cni
git checkout tags/v3.8
```

```
cat ./images/multus-daemonset.yml | kubectl apply -f -
```

Wait for multus pods to become active

### Whereabouts

Log into k8s master

Perform the below steps per this [Installation](https://github.com/k8snetworkplumbingwg/whereabouts/tree/ee60ed15c45d6fcdbccc995caeadb20928cfdadc#installing-whereabouts) guide

```
cd ~
git clone https://github.com/k8snetworkplumbingwg/whereabouts && cd whereabouts
git checkout ee60ed15c45d6fcdbccc995caeadb20928cfdadc
```

```
kubectl apply \
    -f doc/crds/daemonset-install.yaml \
    -f doc/crds/whereabouts.cni.cncf.io_ippools.yaml \
    -f doc/crds/whereabouts.cni.cncf.io_overlappingrangeipreservations.yaml \
    -f doc/crds/ip-reconciler-job.yaml
```

Wait for whereabouts pods to become active

## gtp5g kernel module

Perform the below instructions to install the gtp5g kernel module that will be used by the dataplane function

Do this for all worker nodes on both core and edge clusters

### Install pre-requisites

```
sudo apt-get install libtool
sudo apt-get install pkg-config
sudo apt-get install libmnl-dev
sudo apt install make
sudo apt install net-tools
```

### Build and install

```
cd ~
git clone https://github.com/PrinzOwO/gtp5g && cd gtp5g
git checkout tags/v0.3.2
make clean && make
sudo make install
```

### Set promsic on

Invoke the below against the main network interface

```
sudo ip link set ens3 promisc on
```

## UERANSIM

Perform the below instructions to install ue ran simulator: https://github.com/aligungr/UERANSIM.git

Do this for both gNB and UE VMs

### Clone UERANSIM

```
cd ~
git clone https://github.com/aligungr/UERANSIM.git
cd UERANSIM
git checkout tags/v3.2.0 -b v3.2.0-branch
```

### Install UERANSIM

The below instructions are derived from [ueransim-installation](https://github.com/aligungr/UERANSIM/wiki/Installation)

```
sudo apt install make
sudo apt install gcc
sudo apt install g++
sudo apt install libsctp-dev lksctp-tools
sudo apt install iproute2
sudo snap install cmake --classic
```

Build

```
cd ~/UERANSIM
make
```
