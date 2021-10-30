# Open Cluster Manager

https://open-cluster-management.io/

The following instructions are derived from [here](https://open-cluster-management.io/getting-started/quick-start/)

It is assumed that your managed cluster name is `bcn-core`. For the other cluster (edge) change the name accordingly

## Clusteradm CLI

Install CLI on both hub and clusters to be managed

```
cd ~
wget https://github.com/open-cluster-management-io/clusteradm/releases/download/v0.1.0-alpha.5/clusteradm_linux_amd64.tar.gz
tar xzvf clusteradm_linux_amd64.tar.gz
```

## Deploy a cluster manager on your hub cluster

invoke

```
clusteradm init
```

copy the generated command and replace "managed cluster name" with e.g. `bcn-core`.

### Deploy a klusterlet agent

Log into kubernetes **managed** cluster


and invoke previously join command appending the context of your managed cluster

### Accept join request and verify

Log into kubernetes **hub** cluster

run

```
kubectl get csr -w | grep bcn-core
```

ensure to get output like this

```
bcn-core-tqcjj   33s   kubernetes.io/kube-apiserver-client   system:serviceaccount:open-cluster-management:cluster-bootstrap   Pending
```

accept it

```
clusteradm accept --clusters bcn-core
```

### Verify ManagedCluster CR created successfully

Log into kubernetes **hub** cluster

```
kubectl get managedcluster
```

verify it has true in all corresponding values

### Label cluster with its name

In order to place workloads into this cluster, you need to label it with its name

Log into kubernetes hub cluster

```
kubectl label managedclusters/bcn-core name=bcn-core --overwrite
```

## Subscription controller

The below commands derived from [this](https://open-cluster-management.io/getting-started/integration/app-lifecycle/) guide

Log into kubernetes **hub** cluster

### Install kustomize

https://kubectl.docs.kubernetes.io/installation/kustomize/binaries/

### Install golang (recent version)

https://golang.org/doc/install and select `Linux` tab

### Install the controller

```
git clone https://github.com/open-cluster-management-io/multicloud-operators-subscription
cd multicloud-operators-subscription
```

```
make deploy-hub
```

wait for the operator to run

```
kubectl get pod -n open-cluster-management
```

**Important:**
 
If multicloud-operators-channel deployment pod endters CrashLoopBackOff, edit the deployment to use image tag of: `v0.4.0`. Pod automatically refreshes with new image


### Create agent namespace

Log into kubernetes **managed** cluster

```
kubectl create ns open-cluster-management-agent-addon
```

### Install add-on

Log into kubernetes **hub** cluster

`export MANAGED_CLUSTER_NAME=bcn-core`

```
cd ~/multicloud-operators-subscription
make deploy-addon
```

ensure subscription deployment had been created on the managed cluster

Log into kubernetes **managed** cluster

```
kubectl -n open-cluster-management-agent-addon get deploy multicloud-operators-subscription
```
