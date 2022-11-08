# Applications

This readme is in addition to the [main](./README.md) one 

## Application operators

Similar to the 5G Operator, mentioned in the main readme, there is a folder of application operators (currently for vCache)

Perform the [following](./docs/apps/vcache-operator.md) instructions to install it

Do this for edge clusters application instances are planned to run

## Apply application roles

Do this for all edge clusters application instances are planned to run

Have Argo to run application related workflows under `domain-operator-a` , `domain-operator-b`, `domain-operator-c`, namespaces.

```
cd ~/issm-mec-cnmp
```

```
# operator-a
export NAMESPACE=domain-operator-a
kubectl create namespace $NAMESPACE
envsubst < workflows/argo/apps/role-vcache.yaml.template | kubectl apply -n $NAMESPACE -f -

# operator-b
export NAMESPACE=domain-operator-b
kubectl create namespace $NAMESPACE
envsubst < workflows/argo/apps/role-vcache.yaml.template | kubectl apply -n $NAMESPACE -f -

# operator-c
export NAMESPACE=domain-operator-c
kubectl create namespace $NAMESPACE
envsubst < workflows/argo/apps/role-vcache.yaml.template | kubectl apply -n $NAMESPACE -f -
```

## Deploy an application

Log into OCM hub cluster

```bash
argo -n domain-operator-b  submit workflows/argo-acm/fiveg-app.yaml --parameter-file workflows/argo-acm/app.json --watch
```

wait for the flow to complete

**Note:** it is assumed that a subnetslice, along with a datanetwork, had already been deployed and that the application has an interface to that datanetwork (i.e. via `network_name` in `app.json`)


## Un-deploy the application

to delete the given application invoke the below supplying `fiveg_app_id`

```bash
argo -n domain-operator-b  submit workflows/argo-acm/fiveg-app-delete.yaml -p fiveg_app_id="fiveg-app-abcd12" --watch
```

wait for the flow to complete
