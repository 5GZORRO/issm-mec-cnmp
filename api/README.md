# Api service

Component responsible for providing management API endpoint service for ISSM-MEC-CNMP.

## Deploy the service

Log into OCM cluster

```
export REGISTRY=docker.pkg.github.com
export IMAGE=$REGISTRY/5gzorro/issm-mec-cnmp/api-server:test
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
  "cluster_core": "bcn-core",
  "cluster_edge": "bcn-edge",
  "smf_name": "smf-sample",
  "sst": "1",
  "sd": "010203"
}'
```

Example 2: slice attached to a local datanetwork

```bash
curl -X POST \
  http://192.168.1.117:30055/subnetslice \
  -H 'content-type: application/json' \
  -d '{
  "cluster_core": "bcn-core",
  "cluster_edge": "bcn-edge",
  "smf_name": "smf-sample",
  "sst": "1",
  "sd": "010203",
  "network_name": "gilan",
  "network_master": "ens3",
  "network_range": "10.20.0.0/24",
  "network_start": "10.20.0.2",
  "network_end": "10.20.0.50"
}'
```



## Build (**relevant for developers only**)

1.  Set the `REGISTRY` environment variable to hold the name of your docker registry. The following command sets it
    equal to the docker github package repository.

    ```
    $ export REGISTRY=docker.pkg.github.com
    ```

1.  Set the `IMAGE` environment variable to hold the image.

    ```
    $ export IMAGE=$REGISTRY/5gzorro/issm-mec-cnmp/api-server:test
    ```

1.  Invoke the below command.

    ```
    $ docker build --tag "$IMAGE" --force-rm=true .
    ```

1.  Push the image.

    ```
    $ docker push "$IMAGE"
    ```
