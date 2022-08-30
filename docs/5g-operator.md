# 5G Operator

Log into kubernetes master

## Clone

```bash
cd ~
git clone https://github.com/5GZORRO/issm-mec-cnmp-5g-operator.git
cd issm-mec-cnmp-5g-operator
git checkout free5gc-v3.1.1
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

## Build (**relevant for developers only**)

1. Edit Makefile with `VERSION ?= temp` so that the resulted image tag does not collide with the existing one.

1. Edit Makefile with `IMAGE_TAG_BASE` with the proper image registry. Note: current version uses an internal registry to hold the operator and 5G network function images.

1. Build and push the image.

    ```
    make generate
    ```
    
    ```
    make manifests
    ```
    
    ```
    make docker-build docker-push
    ```

1. Deploy the operator

   ```
   make deploy
   ```
