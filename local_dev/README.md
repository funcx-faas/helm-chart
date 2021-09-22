# Local Dev

Tools for handling local development workflow.

## Local Dev Deployments

There are two main actions supported by the Makefile in the repo root:

`make dev-up` creates a local cluster using helm, waits for it to be ready, and
starts local kubectl port forwarding.

`make dev-down` tears down any port forwarding and shuts down the helm-launched
cluster.

Note that `make dev-up` uses the `--atomic` flag to `helm install`, meaning
that a failure to start will terminate and cleanup the cluster.

## microk8s configuration

For `microk8s` development, use `kubectl` and `helm` installed outside of
`microk8s`. i.e. We want the commands `helm` and `kubectl`, not
`microk8s kubectl` and `microk8s helm3`.

To do this, take the following steps after installing `microk8s` to install the
tools:

- `snap install kubectl --classic`
- `snap install helm --classic`

> NOTE: You can use non-snap install methods as well. `snap` is presumed here
> only because it is required for `microk8s` installation.

Then write your `microk8s` config into `~/.kube/config` with

    mkdir -p ~/.kube
    microk8s config > ~/.kube/config
    chmod 600 ~/.kube/config

You can also combine `microk8s config` configuration with other kubectl
config if preferred. For cases where you want some other `kubectl` context
(e.g. for use against EKS clusters), combine microk8s config with
existing/other config:

    microk8s config > microk8s-config
    KUBECONFIG=~/.kube/config:./microk8s-config kubectl config view --flatten > tmp
    mv tmp ~/.kube/config
    chmod 600 ~/.kube/config

## Using a Local Image

These instructions will show how to use a custom image for funcx_web_service.
The same principles apply to other pods.

The steps vary a little based on your local kubernetes toolchain.

### Under minikube

TODO: stub

### Under microk8s

1. Build local docker image

To use a local image in microk8s, you will need to build a local image using
`docker`, with no special invocation. Go to the `funcx-web-service` repo and run

    $ docker build --no-cache . -t funcx_web_service:develop

2. Import the image into the microk8s registry

microk8s can do an image import from a `.tar` formatted image. Do either in two
steps:

    $ docker save funcx_web_service > funcx_web_service.tar
    $ microk8s ctr image import funcx_web_service.tar

or as one command:

    $ docker save funcx_web_service | microk8s ctr image import -

3. Set your dev values.yaml to use the image

Use these settings:

```yaml
webService:
  pullPolicy: Never
  image: funcx_web_service
  tag: develop
```
