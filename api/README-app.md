### Create application

Creates an application on a given (edge) kubernetes cluster, connecting it to the given datanetwork (of the slice)

```
curl -X POST -d '{"cluster": "<string>", "kind": <string>, "api_version": <>, "success_condition": <string>, "config": {...}, ...}' http://<ocm master ipaddress>:30055/app

REST path:
    ocm master ipaddress - ipaddress of OCM Hub.

Data payload:
    cluster             - the (edge) cluster of which the subnet will be deployed (str)
    namespace           - the namespace under which the subnet will be deployed (str)

    api_version         - CR api version (for loading application operator SDK) (str)
    kind                - CR kind (for loading application operator SDK) (str)
    success_condition   - application specific CR query to indicate a completion of application deployment (str)
    config              - application specific configuration (json)
    product_id          - the product offer ID of the application (str in uuid/DID format)
    elma_url            - url of license agent (http://<ip>:<port>) to verify that
                          the supplied product_id has a valid license
```

Example (deploying vCache CR):

```bash
curl -X POST \
  http://192.168.1.117:30055/app \
  -H 'content-type: application/json' \
  -d '{
  "cluster": "cluster-1",
  "namespace": "domain-operator-b",
  "api_version": "5g.ibm.com/v1alpha1",
  "kind": "Vcache",
  "success_condition": "status.registered == true",
  "config": {
    "image": "vcache_icom:latest",
    "data_network_name": "gilan"
  },
  "product_id": "EEyymp33AzSYHZFwvT8Bvp",
  "elma_url": "http://172.28.3.42:31880"
}'

{
  "name": "fiveg-app-j7dlm"
}
```
