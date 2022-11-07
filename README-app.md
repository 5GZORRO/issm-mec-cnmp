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
