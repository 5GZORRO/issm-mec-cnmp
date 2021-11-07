# 5GInitContainer

Init container responsible to create service/endpoint objects for multus intefraces of the pod.

The purpose of this init-container is to create DNS records prior to pod application start up. This is done by querying POD's annotation `k8s.v1.cni.cncf.io/network-status` and creating for every multus network, a pair of service and endpoint with the ipaddress. These objects are set to be owned by the parent CR so that they are automatically removed once the CR is deleted.

By the above, we automatically register the network-function service with its IP address, in the coreDNS to be used by the application in the main container.

**Note:** it is confirmed to work with kubernetes `1.19.4`, coreDNS `v1.7.0` 

**Important:** current version assumes that RBAC role for creating service/endpoint is already defined for the namespace'd service-account

### Integrating init container

Init container is being defined by the 5G NFs controller in a similar pattern as below:

```
  initContainers:
    - name: amf-init
      image: artifactory.haifa.ibm.com:5130/weit/5ginitcontainer
      volumeMounts:
        - name: podinfo
          mountPath: /etc/podinfo
      env:
      - name: CR_KIND
        value: "Amf"
      - name: CR_NAME
        value: "amf-sample"
      - name: CR_UID
        value: <parent CR uid>
      - name: DIR
        value: "/etc/podinfo"
      - name: FILE
        value: "annotations"
```

## Build

1.  Set the `REGISTRY` environment variable to hold the name of your docker registry. The following command sets it
    equal to the Haifa repository.

    ```
    $ export REGISTRY=docker.pkg.github.com
    ```

1.  Set the `IMAGE` environment variable to hold the image of the init container.

    ```
    $ export IMAGE=$REGISTRY/5gzorro/issm-mec-cnmp/$(basename $(pwd))
    ```

1.  Invoke the below command.

    ```
    $ docker build --tag "$IMAGE" --force-rm=true .
    ```

1.  Push the image.

    ```
    $ docker push "$IMAGE"
    ```

