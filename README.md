# helm-chart
Helm Chart for Deploying funcX stack

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![NSF-2004894](https://img.shields.io/badge/NSF-2004894-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=2004894)
[![NSF-2004932](https://img.shields.io/badge/NSF-2004932-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=2004932)

This application includes:
* FuncX Web-Service
* Kuberentes endpoint
* Postgres database
* Redis Shared Data Structure

> :warning: **THIS IS A TEST DEPLOYMENT**: The web-service and forwarder can be deployed, while the funcx-endpoint is not yet properly supported

## Preliminaries
The following dependencies must be set up before you can deploy the helm chart:

## FuncX Endpoint

There are two modes in which funcx-endpoints could be deployed:

1. funcx-endpoint deployed outside k8s, connecting to hosted services in k8s
2. funcx-endpoint deployed with k8s (broken currently)

### Deploying funcx-endpoint externally

Install from the `forwarder_rearch_1` branch of the [funcx repo](https://github.com/funcx-faas/funcX)
Here are the steps to install, preferably to your active conda environment:

```shell script
git clone https://github.com/funcx-faas/funcX.git
cd funcX
git checkout forwarder_rearch_1
pip install funcx_sdk
pip install funcx_endpoint
```

Next create an endpoint configuration:

```shell script
funcx-endpoint
```

Update the configuration file to point the endpoint to locally deployed services, which we will setup in the next sections.

    ```python
    config = Config(
    executors=[HighThroughputExecutor(
        provider=LocalProvider(
            init_blocks=1,
            min_blocks=0,
            max_blocks=1,
        ),
    )],
    funcx_service_address="http://127.0.0.1:5000/api/v1", # <--- UPDATE THIS LINE
)

     ```
### Deploying funcx-endpoint into the k8s deployment

> :warning: **THIS IS BROKEN AT THE MOMENT**

We can deploy the kubernetes endpoint as a pod as part of the chart. It
needs to have a valid copy of the funcx's `funcx_sdk_tokens.json` which can
be created by running on your local workstation and running
```shell script
 funcx-endpoint start
```

You will be prompted to follow the authorization link and paste the resulting
token into the console. Once you do that, funcx-endpoint will create a
`~/.funcx` directory and provide you with a token file.

The Kubernetes endpoint expects this file to be available as a Kubernetes
secret named `funcx-sdk-tokens`.

You can install this secret with:
```shell script
pushd ~/.funcx
kubectl create secret generic funcx-sdk-tokens --from-file=credentials/funcx_sdk_tokens.json
popd
```


> :warning: *Only for debugging*: You can set the forwarder curve server key manually by creating
  a public/secret curve pair, registering them with kubernetes as a secret and then specifying
  `forwarder.server_cert = true`. By default the forwarder auto generates keys, and distributes it
  to the endpoint during registration.

To manually setup the keys for debugging, here are the steps:

1. Create your cureve server public/secret keypair with the create_certs.py script:

    ```shell script
    # CD into the funcx-forwarder repo
    python3 test/create_certs.py -d .curve
    ```

2. Similar to the `funcx-sdk-tokens` add the public/secret pair as kubernetes secret:`funcx-forwarder-secrets` for the forwarder service.
```shell script
# Make sure the server.key_secret file is in your $PWD/.curve dir
kubectl create secret generic funcx-forwarder-secrets --from-file=.curve/server.key --from-file=.curve/server.key_secret
```

3. Once the endpoint is registered to the newly deployed `funcx-forwarder`, make sure to check the `~/.funcx/<ENDPOINT_NAME>/certificates/server.key` file to confirm that the manually added key has been returned to the endpoint.

### Forwarder
The forwarder needs to be able to open and manage arbitrary ports which is
not compatible with some of Kubernetes requirements. For now we will run it
as a docker container, but outside of the cluster.

Launch a copy of forwarder outside of kubernetes, listening on port 8080:
    ```shell script
     docker run --rm -it -p 8080:3031 funcx/forwarder:213_helm_chart
    ```

## How to Install FuncX
1. Make a clone of this repository
2. Download subcharts:
    ```shell script
     helm dependency update funcx
    ```
3. Create your own `values.yaml` inside the Git ignored directory `deployed_values/`
4. Obtain Globus Client ID and Secret. Paste them into your values.yaml as
    ```yaml
    webService:
      globusClient: <<your app client>>
      globusKey: <<your app secret>>
    ```
5. Install the helm chart:
    ```shell script
    helm install -f deployed_values/values.yaml funcx funcx
    ```
6. You can access your web service through the ingres or via a port forward
to the web service pod. Instructions are provided in the displayed notes.

7. You should be able to see the endpoint registering with the web service
in their respective logs, along with the forwarder log

## Database Setup
Until we migrate the webservice to use an ORM, we need to set the database
schema up using a SQL script. This is accomplished by an init-container that
is run prior to starting up the web service container. This setup image checks
to see if the tables are there. If not, it runs the setup script.

## Values

> :warning: **USE THE FOLLOWING dev_values.yaml**

``` yaml
webService:
  pullPolicy: Always
  host: http://localhost:5000
  globusClient: <GLOBUS_CLIENT_ID_STRING>
  globusKey: <GLOBUS_CLIENT_KEY_STRING>
  tag: forwarder_rearch_update

endpoint:
  enabled: false
funcx_endpoint:
  image:
    tag: exception

forwarder:
  enabled: true
  tag: forwarder_redesign
  pullPolicy: Always
  local_image: funcx-forwarder-dev1:latest

redis:
  master:
    service:
      nodePort: 30379
      type: NodePort
postgresql:
  service:
    nodePort: 30432
    type: NodePort
```
There are a few values that can be set to adjust the deployed system
configuration

| Value                          | Desciption                                                          | Default           |
| ------------------------------ | ------------------------------------------------------------------- | ----------------- |
| `webService.image`             | Docker image name for the web service                               | funcx/web-service |
| `webService.tag`               | Docker image tag for the web service                                | 213_helm_chart |
| `webService.pullPolicy`        | Kubernetes pull policy for the web service container                | IfNotPresent |
| `webService.dbSetupImage`      | Docker image name for the web service database setup image          | funcx/web-service-db |
| `webService.dbSetupTag`        | Docker image tag for the web service database setup                 | 213_helm_chart |
| `webService.dbSetupPullPolicy` | Kubernetes pull policy for the web service database setup container | IfNotPresent |
| `webService.advertisedRedisPort` | Redis port that the forwarder (outside of cluster) can reach | 6379 |'
| `webService.advertisedRedisHost` | Redis host that the forwarder (outside of cluster) can reach | localhost |'
| `webService.globusClient`      | Client ID for globus app. Obtained from [http://developers.globus.org](http://developers.globus.org) | |
| `webService.globusKey`         | Secret for globus app. Obtained from [http://developers.globus.org](http://developers.globus.org) | |
| `webService.replicas`          | Number of replica web services to deploy                            | 1 |
| `endpoint.enabled`            | Deploy an internal kubernetes endpoint? | true |
| `endpoint.replicas`            | Number of replica endpoint pods to deploy | 1 |
| `endpoint.image`             | Docker image name for the endpoint                               | funcx/kube-endpoint |
| `endpoint.tag`               | Docker image tag for the endpoint                                | 213_helm_chart |
| `endpoint.pullPolicy`        | Kubernetes pull policy for the endpoint container                | IfNotPresent |
| `forwarder.enabled`            | Deploy an internal kubernetes forwarder? | true |
| `forwarder.minInterchangePort`    | The minimum port to assign interchanges. This will be the first port opened int he pod | 54000 |
| `forwarder.maxInterchangePort`    | The maximum port to assign interchanges. Only the first three ports are opened in the pod | 54002 |
| `forwarder.image`             | Docker image name for the forwarder                               | funcx/funcx/forwarder |
| `forwarder.tag`               | Docker image tag for the forwarder                                | dev |
| `forwarder.pullPolicy`        | Kubernetes pull policy for the forwarder container                | IfNotPresent |
| `ingress.enabled`              | Deploy an ingres to route traffic to web app?                       | false |
| `ingress.host`                 | Host name for the ingress. You will be able to reach your web service via a url that starts with the helm release name and ends with this host | uc.ssl-hep.org |
| `postgres.enabled`             | Deploy a postgres instance?                                         | true |

## Subcharts
This chart uses two subcharts to supply dependent services. You can update
settings for these by referenceing the subchart name and values from
their READMEs.

For example
``` yaml
postgresql.postgresqlUsername: funcx
```
| Subchart   | Link to Documentation |
| ---------- | --------------------- |
| postgresql | [https://github.com/bitnami/charts/tree/master/bitnami/postgresql](https://github.com/bitnami/charts/tree/master/bitnami/postgresql) |
| redis      | [https://github.com/bitnami/charts/tree/master/bitnami/redis](https://github.com/bitnami/charts/tree/master/bitnami/redis) |
