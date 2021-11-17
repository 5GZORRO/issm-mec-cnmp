# Api service

Component responsible for providing API endpoints for ISSM-MEC-CNMP.

## Deploy the service

Log into OCM cluster

```
export REGISTRY=docker.pkg.github.com
export IMAGE=$REGISTRY/5gzorro/issm-mec-cnmp/api-server:4659b79
export NAMESPACE=5g-core
export REGISTRY_PRIVATE_FREE5GC=84.88.32.158:5000
```

```
kubectl apply -f deploy/role.yaml -n $NAMESPACE
envsubst < deploy/deployment.yaml.template | kubectl create -n ${NAMESPACE} -f -
kubectl create -f deploy/service.yaml -n $NAMESPACE
```

### Ensure service is reachable

```
curl http://<ocm master ipaddress>:30055/hello
```

## Service APIs

### Create subnetslice

Creates a slice on a given (edge) kubernetes cluster

```
curl -X POST -d '{"cluster_core": "<string>", "cluster_edge": "<string>", "sst": "<string>", "sd": "<string>", "smf_name": <string>}' http://<ocm master ipaddress>:30055/subnetslice

REST path:
    ocm master ipaddress - ipaddress of OCM Hub.

Data payload:
    cluster_core   - the cluster of where the core is deployed (str)
    cluster_edge   - the edge (cluster) of which the subnet will be deployed (str)
    sst            - the sst of the slice e.g. "1" (str)
    sd             - slice differentiator e.g. "010203" (str)
    smf_name       - the name of the SMF function instance to re-configure (str)
    network_name   - the name of the internal network to attach the slice with (str) Optional.
                     note: if provided, the below is required

    network_master - master interface on the worker node (str)
    network_range  - network range in cidr format (str)
    network_start  - start ip in the sequence range (str)
    network_end    - end ip in the sequence range (str)
```

Example 1:

```bash
curl -X POST \
  http://192.168.1.117:30055/subnetslice \
  -H 'content-type: application/json' \
  -d '{
  "cluster_core": "cluster-2",
  "cluster_edge": "cluster-1",
  "smf_name": "smf-sample",
  "sst": "1",
  "sd": "010203",
  "networks": [
    {
        "name": "sbi", "master": "ens3", "range": "10.100.200.0/24",
        "start": "10.100.200.21", "end": "10.100.200.40"
    },
    {
        "name": "up", "master": "ens3", "range": "192.168.1.0/24",
        "start": "192.168.1.251", "end": "192.168.1.253"        
    }
  ]
}'
```

Example 2: slice attached to a local datanetwork

```bash
curl -X POST \
  http://192.168.1.117:30055/subnetslice \
  -H 'content-type: application/json' \
  -d '{
  "cluster_core": "cluster-2",
  "cluster_edge": "cluster-1",
  "smf_name": "smf-sample",
  "sst": "1",
  "sd": "112233",
  "network_name": "gilan",
  "network_master": "ens3",
  "network_range": "10.20.0.0/24",
  "network_start": "10.20.0.2",
  "network_end": "10.20.0.50",
  "networks": [
    {
        "name": "sbi", "master": "ens3", "range": "10.100.200.0/24",
        "start": "10.100.200.21", "end": "10.100.200.40"
    },
    {
        "name": "up", "master": "ens3", "range": "192.168.1.0/24",
        "start": "192.168.1.251", "end": "192.168.1.253"        
    }
  ]
}'

{
  "subnet_name": "fiveg-subnet-112233"
}


```

### Get subnetslice

Retrieve the progress, status and parameters of a given subnet slice

```
curl -X GET http://<ocm master ipaddress>:30055/subnetslice/<subnet_name>

REST path:
    ocm master ipaddress - ipaddress of OCM Hub.
    subnet_name - the name of the subnetslice as being returned from the POST endpoint (str)
```

Example:

```bash
curl -X GET \
  http://192.168.1.117:30055/subnetslice/fiveg-subnet-010203

{
  "name": "fiveg-subnet-010203",
  "phase": "Running",
  "progress": "1/2",
  "workflow_parameters": [
    {
      "name": "registry",
      "value": "84.88.32.158:5000"
    },
    {
      "name": "cluster_core",
      "value": "cluster-2"
    },
    {
      "name": "cluster_edge",
      "value": "cluster-1"
    },
    {
      "name": "smf_name",
      "value": "smf-sample"
    },
    {
      "name": "sst",
      "value": "1"
    },
    {
      "name": "sd",
      "value": "010203"
    },
    {
      "name": "network_name",
      "value": "gilan"
    },
    {
      "name": "network_master",
      "value": "ens3"
    },
    {
      "name": "network_range",
      "value": "10.20.0.0/24"
    },
    {
      "name": "network_start",
      "value": "10.20.0.2"
    },
    {
      "name": "network_end",
      "value": "10.20.0.50"
    }
  ]
}
```

## Build (**relevant for developers only**)

1.  Set the `REGISTRY` environment variable to hold the name of your docker registry. The following command sets it
    equal to the docker github package repository.

    ```
    $ export REGISTRY=docker.pkg.github.com
    ```

1.  Set the `IMAGE` environment variable to hold the image.

    ```
    $ export IMAGE=$REGISTRY/5gzorro/issm-mec-cnmp/api-server:4659b79
    ```

1.  Invoke the below command.

    ```
    $ docker build --tag "$IMAGE" --force-rm=true .
    ```

1.  Push the image.

    ```
    $ docker push "$IMAGE"
    ```
