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
    cluster_core  - TODO (str)
    cluster_edge  - TODO (str)
    sst           - TODO (str)
    sd            - TODO (str)
    smf_name      - TODO (str) Optional
```

Example:

```bash
curl -X POST \
  http://192.168.1.117:30055/subnetslice \
  -H 'content-type: application/json' \
  -d '{
  "cluster_core": "bcn-core",
  "cluster_edge": "bcn-edge",
  "sst": "1",
  "sd": "010203"
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
