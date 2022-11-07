## Apply application roles

Do this for all edge clusters

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

```
argo -n domain-operator-b  submit workflows/argo-acm/fiveg-app.yaml --parameter-file workflows/argo-acm/app.json --watch
```

wait for the flow to complete

**NOTE:** to delete the given application invoke the below setting `fiveg_app_id` to its proper value

```bash
argo -n domain-operator-b  submit workflows/argo-acm/fiveg-app-delete.yaml -p fiveg_app_id="fiveg-app-abcd12" --watch
```
