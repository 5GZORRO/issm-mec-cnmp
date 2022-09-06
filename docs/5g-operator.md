# 5G Operator

Log into kubernetes master

## golang

Install golang **v1.16**: https://golang.org/doc/install

```
cd ~
wget https://go.dev/dl/go1.16.linux-amd64.tar.gz
```

`sudo -s` then

```
rm -rf /usr/local/go && tar -C /usr/local -xzf go1.16.linux-amd64.tar.gz
```

exit sudo, then update profile file and load it:

```
source ~/.profile
```

validate

```
go version
```

## operator-sdk

Install operator-sdk **v1.8.0** from [install-from-github-release](https://sdk.operatorframework.io/docs/installation/#install-from-github-release)

set platform information

```
export ARCH=$(case $(uname -m) in x86_64) echo -n amd64 ;; aarch64) echo -n arm64 ;; *) echo -n $(uname -m) ;; esac)
export OS=$(uname | awk '{print tolower($0)}')
```

download

```
export OPERATOR_SDK_DL_URL=https://github.com/operator-framework/operator-sdk/releases/download/v1.8.0
curl -LO ${OPERATOR_SDK_DL_URL}/operator-sdk_${OS}_${ARCH}
```

install

```
chmod +x operator-sdk_${OS}_${ARCH} && sudo mv operator-sdk_${OS}_${ARCH} /usr/local/bin/operator-sdk
```

## Deploy the operator

clone

```bash
cd ~
git clone https://github.com/5GZORRO/issm-mec-cnmp-5g-operator.git
cd issm-mec-cnmp-5g-operator
git checkout free5gc-v3.1.1
```

*Note*: you may need to update Makefile to point to correct private image registry

```bash
make generate
make manifests
make deploy
```

**Note:** install gcc (`sudo apt-get install gcc`) incase you encounter the bellow error for `make generate`: `/usr/local/go/src/net/cgo_linux.go:12:8: no such package located`

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
