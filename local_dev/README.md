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

## microk8s shims

For `microk8s` development, we need to handle the fact that commands are
namespaced, but the results will not be compatible with shared scripts.
For example, with `helm` installed under `microk8s`, you have the command
`microk8s helm3`.

While we could write all of our dev tooling to be microk8s-friendly, it is
simpler for any `microk8s` users to add shims as follows.

In `~/.microk8s-shims/helm`:
```
#!/bin/bash
exec microk8s helm3 "$@"
```

In `~/.microk8s-shims/kubectl`:
```
#!/bin/bash
exec microk8s kubectl "$@"
```

and add `~/.microk8s-shims` to their `PATH`.

> NOTE: in case it is not obvious, the exact dirname does not matter. If you
> use another location already for custom tools, such as `~/bin/` or
> `~/.local/bin/`, that would be acceptable for this purpose as well.

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

    $ docker build . -t funcx_web_service:develop

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
