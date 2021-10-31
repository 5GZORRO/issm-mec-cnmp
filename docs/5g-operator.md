# 5G Operator

Log into kubernetes master

## Clone

```bash
cd ~
git clone https://github.com/5GZORRO/issm-mec-cnmp-5g-operator.git
cd issm-mec-cnmp-5g-operator
```

## golang

Install golang **v1.16**: https://golang.org/doc/install

then issue

```
source ~/.profile
```

validate

```
go version
```

## operator-sdk

Install operator-sdk **v1.8.0** from [install-from-github-release](https://sdk.operatorframework.io/docs/installation/#install-from-github-release)

## Deploy the operator

```bash
make generate
make manifests
make deploy
```

Wait for controller pod to start

```
kubectl get pod -n 5g
```

**Notes:** 

* before using 'make', load your profile: `source ~/.profile`
* to un-install the operator: `make undeploy`
