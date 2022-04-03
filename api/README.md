# Api service

Component responsible for providing API endpoints for ISSM-MEC-CNMP.

**Important:** on every `fiveg-***` workflow modification - rebuild and tag the image accordingly

## Deploy the service

Log into OCM cluster

Invoke the below in this order

**Note:** you may need to update below settings according to your environment

```
export REGISTRY=docker.pkg.github.com
export IMAGE=$REGISTRY/5gzorro/issm-mec-cnmp/api-server:79a5f37
export NAMESPACE=issm-mec-cnmp
export REGISTRY_PRIVATE_FREE5GC=84.88.32.158:5000
```

```
export KAFKA_HOST=172.28.3.196
export KAFKA_PORT=9092
```

Deploy

```
kubectl create ns $NAMESPACE
kubectl apply -f deploy/role.yaml -n $NAMESPACE
envsubst < deploy/deployment.yaml.template | kubectl create -n ${NAMESPACE} -f -
kubectl create -f deploy/service.yaml -n $NAMESPACE
```

### Ensure service is reachable

```
curl http://<ocm master ipaddress>:30055/hello
```

## Service APIs

### Create core

Creates a core on a given (core) kubernetes cluster

```
curl -X POST -d '{"cluster_core": "<string>"}' http://<ocm master ipaddress>:30055/core

REST path:
    ocm master ipaddress - ipaddress of OCM Hub.

Data payload:
    cluster        - the cluster of where the core is deployed (str)
    namespace      - the namespace under which the core will be deployed (str)
```

Example:

```bash
curl -X POST \
  http://192.168.1.117:30055/core \
  -H 'content-type: application/json' \
  -d '{
  "cluster": "cluster-2",
  "namespace": "domain-operator-a",
  "networks": [
      {
          "name": "sbi", "master": "ens3", "range": "10.100.200.0/24", "start": "10.100.200.2", "end": "10.100.200.20"
      },
      {
          "name": "ngap", "master": "ens3", "range": "192.168.1.0/24", "start": "192.168.1.250", "end": "192.168.1.250"
      }
  ]
}'

{
  "name": "fiveg-core-pgq4v"
}
```


### Create subnetslice

Creates a slice on a given (edge) kubernetes cluster

```
curl -X POST -d '{"cluster_core": "<string>", "cluster_edge": "<string>", "sst": "<string>", "sd": "<string>", "smf_name": <string>}' http://<ocm master ipaddress>:30055/subnetslice

REST path:
    ocm master ipaddress - ipaddress of OCM Hub.

Data payload:
    cluster        - the (edge) cluster of which the subnet will be deployed (str)
    cluster_core   - the cluster of where the core is deployed (str)
    namespace      - the namespace under which the subnet will be deployed (str)
    sst            - the sst of the slice e.g. "1" (str)
    sd             - slice differentiator e.g. "010203" (str)
    smf_name       - the name of the SMF function instance to re-configure (str)
    core_namespace - the namespace of the 5G core (str)
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
  "cluster": "cluster-1",
  "cluster_core": "cluster-2",
  "namespace": "domain-operator-b",
  "smf_name": "smf-sample",
  "core_namespace": "domain-operator-a",
  "sst": "1",
  "sd": "010203",
  "pool": "60.61.0.0/16",
  "connectedFrom": "gNB",
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
  "name": "fiveg-subnet-j7dlm"
}
```

Example 2: slice attached to a local datanetwork

```bash
curl -X POST \
  http://192.168.1.117:30055/subnetslice \
  -H 'content-type: application/json' \
  -d '{
  "cluster": "cluster-1",
  "cluster_core": "cluster-2",
  "namespace": "domain-operator-c",
  "smf_name": "smf-sample",
  "core_namespace": "domain-operator-a",
  "sst": "1",
  "sd": "112233",
  "pool": "60.62.0.0/16",
  "connectedFrom": "gNB",
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
  "name": "fiveg-subnet-7s9nc"
}
```

### Get core/slice

Retrieve the progress, status and parameters of a given core/slice

```
curl -X GET http://<ocm master ipaddress>:30055/core_subnetslice/<namespace>/<name>

REST path:
    ocm master ipaddress - ipaddress of OCM Hub.
    namespace   - the namespace of the subnetslice
    name - the name of the core/subnetslice as being returned from the POST endpoint (str)
```

Example:

```bash
curl -X GET \
  http://192.168.1.117:30055/core_subnetslice/domain-operator-b/fiveg-subnet-j7dlm

{
  "name": "fiveg-subnet-j7dlm",
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
      "name": "cluster",
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

### Delete slice

Delete a given slice

```
curl -X DELETE http://<ocm master ipaddress>:30055/subnetslice/<namespace>/<name>

REST path:
    ocm master ipaddress - ipaddress of OCM Hub.
    namespace   - the namespace of the subnetslice
    name - the name of the subnetslice as being returned from the POST endpoint (str)
```

Example:

```bash
curl -X DELETE \
  http://192.168.1.117:30055/subnetslice/domain-operator-b/fiveg-subnet-j7dlm
```

## Build (**relevant for developers only**)

1.  Set the `REGISTRY` environment variable to hold the name of your docker registry. The following command sets it
    equal to the docker github package repository.

    ```
    $ export REGISTRY=docker.pkg.github.com
    ```

1.  Set the `IMAGE` environment variable to hold the image.

    ```
    $ export IMAGE=$REGISTRY/5gzorro/issm-mec-cnmp/api-server:79a5f37
    ```

1.  Invoke the below command.

    ```
    $ docker build --tag "$IMAGE" --force-rm=true .
    ```

1.  Push the image.

    ```
    $ docker push "$IMAGE"
    ```
