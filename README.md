# A Chart for Deploying the funcX stack

## Who is this README for?

This README is aimed at people who want to deploy funcX services into
kubernetes, using the helm chart contained in this repository.

The main part of the text is aimed at a new funcX developer making their
first install for themselves to hack on.

Other notes on the way talk about how the install can be made in the
production system at AWS, and in development environments hosted at AWS.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![NSF-2004894](https://img.shields.io/badge/NSF-2004894-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=2004894)
[![NSF-2004932](https://img.shields.io/badge/NSF-2004932-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=2004932)


## Components

A funcx install consists of a number of components, which will each be installed by this chart.

* FuncX Web-Service
* FuncX Websocket Service
* FuncX Forwarder
* Kubernetes endpoint
* Postgres database
* Redis Shared Data Structure
* RabbitMQ broker

## Kubernetes pre-requisites

You will need a Kubernetes (k8s) installation. There is no particularly
favoured form of setup. Some ways used by funcX developers include:

* minikube on a hetzner cloud node
* docker desktop
* microk8s

You will also need `helm`.

You will maybe need an ingress controller - traditionally people haven't been
using one but we are pushing on that a bit. More later.

### Example install of hetzner cloud + minikube

This shows how @benclifford installed minikube on a hetzner cloud node as
root:


Base os: Ubuntu 20.04.03

```
# apt-get install docker.io
# curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
# install minikube-linux-amd64 /usr/local/bin/minikube

# apt-get install contrack   # because: ❌  Exiting due to GUEST_MISSING_CONNTRACK: Sorry, Kubernetes 1.22.1 requires conntrack to be installed in root's path

# minikube --driver=none    # because i am root in a VM. otherwise apparently driver=docker might be nice? I haven't tried
```

Now can run to see running pods

```
# minikube kubectl -- get pods -A
```

This gives me 7 runnings k8s pods.

Now install helm, following debian/apt instructions here: https://helm.sh/docs/intro/install/

```
curl https://baltocdn.com/helm/signing.asc | sudo apt-key add -
sudo apt-get install apt-transport-https --yes
echo "deb https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm
```

How you can run this to see the default helm help text to check it was installed:


```
# helm
```


TODO: is there a "hello world" style helm+kubernetes validation that could be run so
that we can say "you need helm+kubernetes at least good enough to do this:"


Now cloen the funcx helm repo (which you are reading this document from, perhaps):

```
mkdir src
cd  src
git clone git@github.com:funcx-faas/helm-chart
cd helm-chart
```

and run a helm command to update funcx dependencies:

```
helm dependency update funcx
```

which will download some stuff. (TODO: what?)

One note for later is this step downloads a funcx_endpoint chart: although
this is funcX related, it is a separately versioned component because end users
are expected to deploy the endpoint - unlike the funcX services that this
current chart describes. (TODO: notes later for overriding this for
development)


### Configuring a funcx-endpoint in the K8s deployment

TODO: this is messy and not part of the service install so i'm not sure
if it should happen here or as part of the configuration section?

We can deploy the kubernetes endpoint as a pod as part of the chart. It
needs to have a valid copy of the funcx's `funcx_sdk_tokens.json` which can
be created by running on your local workstation and running
```shell script
 funcx-endpoint start
```

(or if I don't have this on my local workstation because I'm deploying purely
inside kubernetes...? can I run this as a command inside minikube - eg after I've
got this running?
yes, with lots of error messages to ignore, I did this:

docker run --rm -ti funcx/kube-endpoint:main /home/funcx/boot.sh funcx

but how then did I get the token out?
)

You will be prompted to follow the authorization link and paste the resulting
token into the console. Once you do that, funcx-endpoint will create a
`~/.funcx` directory and provide you with a token file.

The Kubernetes endpoint expects this file to be available as a Kubernetes
secret named `funcx-sdk-tokens`.

You can install this secret with:
```shell script
kubectl create secret generic funcx-sdk-tokens \
  --from-file ~/.funcx/credentials/funcx_sdk_tokens.json
```

## Installing FuncX ["central services"? what's the right title vs the endpoint and client?]

0. Update cloudformation stack if necessary [TODO: I think this is only for production deployment? ask Josh. In which case, ignore for personal dev cluster]

1. Make a clone of this repository
2. Download subcharts:
    ```shell script
     helm dependency update funcx
    ```
3. Create your own `values.yaml` inside the Git ignored directory `deployed_values/`
     [forward reference to the two different values sections later on in this
      document: should I just have the three lines mentioned here? or should I
      be copy-pasting a huge example?]
   [TODO: paragraph desribing what values.yaml will do]


3a. Obtain Globus Client ID and Secret. Get the credentials by asking on the
   `dev` funcx Slack channel.

   Once you have your credentials, paste them into your `values.yaml`:
    ```yaml
    webService:
      globusClient: <<your app client>>
      globusKey: <<your app secret>>
    ```

   [TODO: there are plans afoot to make this different for developers. When
   that is settled, can reuse deleted text, and elaborate:
   These secrets need to exist in the correct Globus Auth app. 
   ]

3b. Configure endpoint UUID:

    First generate a UUID, for example, by running `uuidgen` or `cat /proc/sys/kernel/random/uuid`.

    Do not copy someone elses UUID from their example configuration. All kinds of subtle identity
    problems will happen if you do.

    Paste the UUID into your values.yaml in an endpoint section:

    ```
    funcx_endpoint:
        endpointUUID: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
    ```

5. Install the helm chart:
    ```shell script
    helm install -f deployed_values/values.yaml funcx funcx
    ```

5b.
now i see a bunch of services including a funcx endpoint, like this:

```
# minikube kubectl get pods
NAME                                            READY   STATUS    RESTARTS         AGE
funcx-endpoint-86756c48c8-flhqf                 1/1     Running   0                95m
funcx-forwarder-db744678c-fqxhg                 1/1     Running   0                95m
funcx-funcx-web-service-97585d958-6zrvh         1/1     Running   0                95m
funcx-funcx-websocket-service-bb766fbcd-rvbgj   1/1     Running   0                95m
funcx-postgresql-0                              1/1     Running   0                95m
funcx-rabbitmq-0                                1/1     Running   0                95m
funcx-redis-master-0                            1/1     Running   0                95m
funcx-redis-slave-0                             1/1     Running   0                95m
funcx-redis-slave-1                             1/1     Running   0                95m
```

6. You should be able to see the endpoint registering with the web service
in their respective logs, along with the forwarder log. Check the endpoint's
logs for its ID. 

7. You can access your funcX services through the ingress or via a port forward
to the web service pod. For port forwarding, instructions are provided in the displayed notes.
[ingress should become the official way, and be better documented, but there is less
experience with it and it needs an ingress controller...]


[clarify which logs / *where* those logs are? explicitly which (3?) logs to
look at... - who is registering with whom?]

Endpoint log will look like:
```
2021-09-14 16:36:02 endpoint.endpoint_manager:172 [INFO]  Starting endpoint with uuid: cfd389f3-4eda-413b-af95-4d54a8e944dc
```

forwarder will look like:
```
{"asctime": "2021-09-14 18:20:44,535", "name": "funcx_forwarder.forwarder", "levelname": "DEBUG", "message": "endpoint_status_message", "log_type": "endpoint_status_message", "endpoint_id": "cfd389f3-4eda-413b-af95-4d54a8e944dc", "endpoint_status_message": {"_payload": null, "_header": "b'\\xcf\\xd3\\x89\\xf3N\\xdaA;\\xaf\\x95MT\\xa8\\xe9D\\xdc'", "ep_status": {"task_id": -2, "info": {"total_cores": 0, "total_mem": 0, "new_core_hrs": 0, "total_core_hrs": 0, "managers": 0, "active_managers": 0, "total_workers": 0, "idle_workers": 0, "pending_tasks": 0, "outstanding_tasks": {}, "worker_mode": "no_container", "scheduler_mode": "hard", "scaling_enabled": true, "mem_per_worker": null, "cores_per_worker": 1.0, "prefetch_capacity": 10, "max_blocks": 100, "min_blocks": 1, "max_workers_per_node": 1, "nodes_per_block": 1}}, "task_statuses": {}}}
```

web service will look like:
```
{"asctime": "2021-09-14 16:36:03,273", "name": "funcx_web_service", "levelname": "INFO", "message": "Successfully registered cfd389f3-4eda-413b-af95-4d54a8e944dc in database"}
```

## Exposing FuncX to external clients and endpoints

You need to expose two ports from your cluster to clients. There are two ways:
ingress and port-forward. These instructions talk about ingress, which is more
complicated to set up but easier to maintain and closer to the production
configuration. If you do not configure ingress, then the post-install notes
output by `helm install` will tell you which port-forward commands to run.

1. Install an ingress controller. Minikube and microk8s do this differently.

1.a Minikube:

Run this:

```
minikube addons enable ingress
```

1.b microk8s

Run this:

```
microk8s enable ingress
```

Then configure microk8s to serve all namespaces. (by default, it only
serves the `public` ingress class). [TODO: i need to write the exact commands for this]

2. Get a hostname that your kubernetes install is accessible under.

Depending on your development environment, this might be the public hostname of your
kubernetes server, or it might be an entry in `/etc/hosts` pointing to 127.0.0.1.
Maybe even `localhost` works in that case.

3. Enable ingress in the funcx install

Edit `deployed_values/values.yaml` to enable funcx ingress and to tell funcx the
host name from step 2.

```
ingress:
  enabled: true
  host: amber.cqx.ltd.uk
```

4. Redeploy funcx

```
helm upgrade --atomic -f deployed_values/values.yaml funcx funcx
```

### Connecting clients

Create a `FuncXClient` instance pointing at your install, by specifying the funcx_service_address,

```
fxc = FuncXClient(funcx_service_address="http://amber.cqx.ltd.uk:8000/v2")
```

and by specifying your endpoint UUID (generated earlier) when invoking a function.

Run the same sort of tests as can happen against the tutorial endpoint. For example:

```
from funcx.sdk.client import FuncXClient

fxc = FuncXClient(PARMS HERE)

def hello_world():
  return "Hello World!"

func_uuid = fxc.register_function(hello_world)

tutorial_endpoint = 'YOUR-ENDPOINT-UUID-HERE'
result = fxc.run(endpoint_id=tutorial_endpoint, function_id=func_uuid)

print(fxc.get_result(result))
```

If you have got this far, then you have successfully installed the current
version of funcx, and can begin to hack.


[TODO: at this point I got into a lot of tangle with default Python versions
not matching up. We've subsequently talked and fiddled with this - so check
what will happen. In the meantime skip these notes:

this gets as far as submitting for me, but attempts to get the result always give
funcx.utils.errors.TaskPending: Task is pending due to waiting-for-nodes

There's a pod started up ok - called funcx-1631645705407 without any more interesting name. i guess thats a worker? after 106s all that is in the logs is a warning from pip running as root
- but i can see pip running.

So i should put a note here about how long things might take here?
Note that it has changes from waiting-for-ep in the error to waiting-for-nodes
after several minutes, so there is more stuff going on, slowly... 5m later and its still churning. it's had one restart 63s ago... nothing clear about *why* it restarted though.
in kubectl describe pod XXXXX I can see the commandline - a pip install and then a funcx-manager.
It seems to end with: PROCESS_WORKER_POOL main event loop exiting normally

So lets debug a bit more about where the task execution happens or not.

Is this doing a pip install on every restart (?!) - that's a question to ask.
(maybe it's not actually installing new stuff though - which is why i'm not seeing any
packages being installed on subsequent runs)

Eventually it went into "CrashLoopBackOff" at the kubernetes level, which maybe isn't the right behaviour for "exiting normal" at the PROCESS_WORKER_POOL level? Ask on chat about that.

There's nothing in the endpoint logs about starting up that funcx process worker container, or about jobs happening - just every 600s a keepalive message

Digging into the endpoint container environment, find ~/.funcx/funcx/EndpointInterchange.log
which is reporting a sequence of errors:

2021-09-15 14:26:55.592 funcx_endpoint.executors.high_throughput.executor:540 [WARNING]  [MTHR
EAD] Executor shutting down due to version mismatch in interchange
2021-09-15 14:26:55.610 funcx_endpoint.executors.high_throughput.executor:542 [ERROR]  [MTHREA
D] Exception: Task failure due to loss of manager b'18e00d57935c'
NoneType: None
2021-09-15 14:26:55.610 funcx_endpoint.executors.high_throughput.executor:577 [INFO]  [MTHREAD
] queue management worker finished

then every 10ms this message *forever* 2021-09-15 14:26:55.613 funcx_endpoint:504 [ERROR]  [MAIN] Something broke while forwarding re
sults from executor to forwarder queues
Traceback (most recent call last):
  File "/usr/local/lib/python3.7/site-packages/funcx_endpoint/endpoint/interchange.py", line 4
90, in _main_loop
    results = self.results_passthrough.get(False, 0.01)
  File "/usr/local/lib/python3.7/multiprocessing/queues.py", line 108, in get
    res = self._recv_bytes()
  File "/usr/local/lib/python3.7/multiprocessing/connection.py", line 216, in recv_bytes
    buf = self._recv_bytes(maxlength)
  File "/usr/local/lib/python3.7/multiprocessing/connection.py", line 407, in _recv_bytes
    buf = self._recv(4)
  File "/usr/local/lib/python3.7/multiprocessing/connection.py", line 383, in _recv
    raise EOFError
EOFError

- that kind of failure should be resulting in a kubernetes level restart (or some other exit/restart) not a hang loop like this?
- mismatch of what? between who? is it the process worker pool container vs the funcx container?  Looking at interchange.py - this might not even be from a version mismatch: it can happen if reg_flag is false (due to a json deserialisation problem in registration message). Other than that, it can happen because the python versions from the manager vs the interchange.

I commented on these logs not being obvious, in slack, and ben g gave me:
> so for debugging, I added a value to the endpoint helm chart detachEndpoint -since the endpoint runs in a daemon, the output doesn’t show up in the pod’s logs.. Setting this to false means the endpoint runs in the main thread. Less reliable, but easy for debugging

I haven't tried that yet. But if its good, then... if k8s endpoints are also expected for end users, maybe they should also get the same functionality? (eg why is this running as a daemon when its inside a pod anyway managing that?)

whle the task on the client side still reports:
funcx.utils.errors.TaskPending: Task is pending due to waiting-for-ep

At the same time, the process worker service repeatedly exits and is restarted by kubernetes (with it eventually hitting CrashLoopBackOff to slow this down) - presumably that's somehow opposite half of this same error message, but it isn't clear. The entire log file is:

root@amber:~# minikube kubectl logs -- funcx-1631715998878
WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv
PROCESS_WORKER_POOL main event loop exiting normally
root@amber:~# 

I found a more interesting log file here:
/home/funcx/.funcx/funcx/HighThroughputExecutor/worker_logs/8e8f66c705d3/manager.log

which eventully reports a critical error that the interchange heartbeat is missing - not at all like the kubectl log error of: ... exiting normally.

It's a bit weird to be 2 minutes in before the manager even notices that the interchange isn't even alive.

So... the version mismatch:
This is invoking python:3.6-buster - so let's track down where that was.

Selecting the correct image (eg for AWS AMIs, not docker images) has been a massive
usability problem for testing parsl on image based systems... I'm not sure how much it
matters in end-use though, if you're assuming that users make app-specific images that
are tied to their own environment? I don't have experience there.  I haven't spent any
time seriously trying to solve this for parsl, but eg ZZ did container stuff for parsl
so I'd be interested to here any of his relevant experiences. not really a  problem
i am interested in solving.

so grep around in the source tree for python:3.6-buster

The funcx endpoint helm chart is coming from a URL on funcx.org, not the helm-charts repo,
under here: http://funcx.org/funcx-helm-charts

There's a 0.3 chart in the funcx-helm-charts repo by the looks of it - perhaps I can try that, by hacking at the server-side chart. What's the right way to be controlling this?

While checking if process claims to be alive, the endpoint output line:
"funcx-endpoint process is still alive. Next check in 600s." 
should be given a timestamp - it doesn't seem to go through the logging mechanism so
is not getting a timestamp that way. So I have no idea when it last ran, or if its
an outdated message, etc.

This command to install the worker inside the worker container is installing funcx-endpoint and directing the output to a file called =0.2.0. That is probably not what is intended. Put the whole thing in ' marks perhaps.

      pip install funcx-endpoint>=0.2.0

This is in the funcx endpoint helm chart... along with the naughty command right next
to it:
workerImage and 
workerInit
so I should be able to override those myself in my values.yaml?

funcx_endpoint:
  workerImage: python:3.7-buster
  workerInit: 'pip install "funcx-endpoint>=0.2.0"'

note that workerInit is embedded python string syntax, not a plain string, so
you can't use ' marks inside it because it is substituted in somewhere I think
and that causes a syntax error - eg try the above line with " and ' swapped
and see:
"""
File "/home/funcx/.funcx/funcx/config.py", line 24
    worker_init='pip install 'funcx-endpoint>=0.2.0'',
                                  ^
SyntaxError: invalid syntax
"""
because string substitution into source without proper escaping.

This could be fixed - either by reading the string from a different place and
not doing python source substitution, or by performing escaping on the string.
This behaviour is likely to cause trouble to anyone doing non-trivial bash
in their worker_init.

it's frustrating that the python version is not set to the version that
is actually used by the endpoint.
]

### Forwarder Debugging

> :warning: *Only for debugging*: You can set the forwarder curve server key manually by creating
  a public/secret curve pair, registering them with kubernetes as a secret and then specifying
  `forwarder.server_cert = true`. By default the forwarder auto generates keys, and distributes it
  to the endpoint during registration.

To manually setup the keys for debugging, here are the steps:

1. Create your curve server public/secret keypair with the create_certs.py script:

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


## Specifying more configuration values

Default configuration values come from `funcx/values.yaml`. These can be
overridden per-deployment by placing replacements in the non-version-controlled
`deployed_values/values.yaml` - for example, the globusClient/globusKey values
earlier in the install instructions.

This is a recommended [TODO: by whom?] initial set of values to override:

should I use the following values.yaml or the values.yaml I was told to make earlier?
dedupe - and if this section is the values.yaml i should be using, move it up to
where i am told to create the values.yaml

eg. why do I need to be exposing postgres to the internet?

``` yaml
webService:
  globusClient: <GLOBUS_CLIENT_ID_STRING>
  globusKey: <GLOBUS_CLIENT_KEY_STRING>

# Note that we install numpy into the worker so that we can run tests against the local 
# deployment
# Note that the workerImage needs the same python version as is used in the funcx_endpoint 
# image.
funcx_endpoint:
  image:
    pullPolicy: Always
    tag: main
  maxBlocks: 2
  initBlocks: 0
  minBlocks: 2
  workerInit: pip install funcx-endpoint==0.3.2 numpy
  workerImage: python:3.7-buster

rabbitmq:
  auth:
    erlangCookie: c00kie
  pullPolicy: Always
```

Here are some more values that can be set to adjust the deployed system
configuration:


| Value                          | Desciption                                                          | Default           |
| ------------------------------ | ------------------------------------------------------------------- | ----------------- |
| `secrets`                      | Name of a secret deployed into the cluster. Must follow example_secrets.yaml | -        |
| `webService.image`             | Docker image name for the web service                               | funcx/web-service |
| `webService.tag`               | Docker image tag for the web service                                | 213_helm_chart |
| `webService.pullPolicy`        | Kubernetes pull policy for the web service container                | IfNotPresent |
| `webService.loglevel`          | Setting for the App logging level                                   | DEBUG          |
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
| `services.postgres.enabled`      | Deploy postgres along with service?                             | true |
| `services.postgres.externalURI`  | If postgres is deployed externally, what URI connects to it?    | sqlite:////sqlite/app.db |
| `services.redis.enabled`         | Deploy redis along with service?                             | true |
| `services.redis.externalHost`  | If redis is deployed externally, what is the host name?    |  |
| `services.redis.externalPort`  | If redis is deployed externally, what is the port?    |  6379 |
| `storage.awsSecrets`           | Name of Kubernetes secret that holds the AWS credentials |    |
| `storage.s3Bucket`             | S3 bucket where storage will write results and payloads | funcx |
| `storage.redisThreshold`       | Threshold to switch large results to S3 from redis (in bytes) | 20000 |
| `storage.s3ServiceAccount`     | Kubernetes Service Account to use for accessing AWS access tokens (blank to skip service account) | <blank> |


## Sealed Secrets
[TODO: why would i want to do this?]
The chart can take advantage of Bitnami's sealed secrets controller to encrypt
sensitive config data so it can safely be checked into the GitHub repo.

Create a secrets.yaml file with these values (the values need to be base64 
encoded (use `echo "secret value" | base64`)). Use the file [example_secrets.yaml](example_secrets.yaml) to see
how the file should be formatted and the names of the secrets.

With kubectl configured to talk to the target cluster, encode the secrets file
with the command:
```console
cat local-dev-secrets.yaml | \
        kubeseal --controller-namespace kube-system \
        --controller-name sealed-secrets \
        --format yaml > local-dev-sealed-secrets.yaml
```

## AWS Secrets for S3 Storage

The globus accounts need a role change before you get the keys, before your default
account usually doesn't come with many privileges. The script below fetches your keys and
creates yaml file that can be installed into your cluster:

Example yaml for references:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysecret
type: Opaque
data:
  AWS_ACCESS_KEY_ID: <<base64 encoded access key>>
  AWS_SECRET_ACCESS_KEY: <<base64 encoded secret>>
  AWS_SESSION_TOKEN: |-
    <<base64
    encoded
    multiline
    session_token>>
```

```bash

# First get the target role ARN

# assuming that you are using assume-role configuration in ~/.aws/config , you
# can get this from your current profile's role_arn value
# if you are not using assume-role to access the account where you intend to
# access an S3, these steps may vary
role_arn=$(aws configure get 'role_arn')
echo "Role Arn: $role_arn"


# parse sts assume-role output into a shell array (works in bash, zsh)
# you can `echo "${credarr[1]}"` to see the access key, for example
credarr=("$(aws sts assume-role \
    --role-arn "$role_arn" --role-session-name test1 \
    --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
    --output text | tr '\t' '\n')")

# base64 encode these credentials
access_key_id=$(echo -n "${credarr[1]}" | base64)
secret_key=$(echo -n "${credarr[2]}" | base64)
session_token=$(echo -n "${credarr[3]}" | base64)

cat <<EOF > secret.token.yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysecret
type: Opaque
data:
  AWS_ACCESS_KEY_ID: $access_key_id
  AWS_SECRET_ACCESS_KEY: $secret_key
  AWS_SESSION_TOKEN: |-
    $session_token
EOF
```


## Subcharts
This chart uses two subcharts to supply dependent services. You can update
settings for these by referencing the subchart name and values from
their READMEs. [TODO: also the funcx endpoint subchart?]

For example
``` yaml
postgresql.postgresqlUsername: funcx
```
| Subchart   | Link to Documentation |
| ---------- | --------------------- |
| postgresql | [https://github.com/bitnami/charts/tree/master/bitnami/postgresql](https://github.com/bitnami/charts/tree/master/bitnami/postgresql) |
| redis      | [https://github.com/bitnami/charts/tree/master/bitnami/redis](https://github.com/bitnami/charts/tree/master/bitnami/redis) |


## Helpful Scripts
It's common for the database to have limited external access. In this case it's
easier to create a busy-box inside the cluster and access plsql internally.

In the scripts directory there is `psql-busybox.yaml`. Create the pod with 
```console
$ kubectl create -f scripts/psql-busybox.yaml
```

You can then create a shell with `kubectl exec -it plsql bash`

Inside that shell there is a fun pg sql client which can be invoked with the
same Postgres URL found in the web app's config file (`/opt/funcx/app.conf`)

```console
pgcli postgresql://funcx:XXXXXXXXXXXX@funcx-production-db.XXXXXX.rds.amazonaws.com:5432/funcx
```
[if this is intended to be used inside a dev cluster, is there a better way to name
the DB than this rd.amazonaws url?

Where does the XXXX password come from in a dev cluster?
Here's a better command line for my minikube setup:

root@plsql:/# pgcli postgresql://funcx:leftfoot1@funcx-postgresql:5432/public



## Upgrades
[TODO: crossref/ incorporate text from the helm upgrade that happens in the
ingress section above
]

# General benc grumbles to address

How does I upgrade this? It was installed using the latest images at install time I guess?
I see a funcx-web-service tag from 15h ago after running helm upgrade funcx funcx...
(imgage ID d21432c1525a) - so is that what is running now? looks like it pulled a new image when I rebooted the server (!)

That seems a bit chaotic. And how do I switch these to using my own source builds?


python versions:
 The endpoint repo funcX/Dockerfile-endpoint defaults to building with python 3.8.
 That doesn't align with the python that is being supplied by the helm images.
 So rebuild my client, specifying 3.7.

Perhaps funcx/Dockerfile-endpoint should force the user to choose, rather than building
a likely invalid one.

The broad topic here is python versions are poorly co-ordinated as supplied - yes, they
have to align, but the defaults supplied should all align with each other at least.
(they need to align across all three of: the submitting client, the endpoint, the
endpoint workers, and all three are wrong by default)


Python mismatch between interchange and worker pod results in an eternal hang: interchange reports inside its endpoint logs that there's a version mismatch (but not what the version mismathc is). The worker just restarts every couple of minutes with missing heartbeat: no description of *why* the heartbeat is missing. The end user is never informed of anything more than "waiting for nodes". It's unclear to me if that should be a richer message or a richer hard error: could tell user that the worker version is wrong at least, becaues that is likely an error that won't fix itself (i.e. is not a transient error). Richer error here would help the submitting user understand that they need to contact the endpoint administrator for rectification and what to tell them, beyond "waiting for nodes".


funcx endpoint worker pods lose their logs at each restart - which is awkward to examine when the logs are in an every-two-minutes restart loop due to missing heartbeat. debuggability might be enhanced by putting them in a pod-lifetime dir rather than a container-lifetime dir? [should they even be autorestarting in that situation, rather than letting the endpoint handle restarting them if it still wants them? - c.f. parsl discussion about how kubernetes pods are managed by the parsl kubernetes provider?] 



## Upgrading and developing against non-main environments

i've been trying this but it's not clear that it is pulling down the latest of
everything: (I think it does, but just the images are not changing often
upstream from me?)
 helm upgrade -f deployed_values/values.yaml funcx funcx --recreate-pods

## Python version notes

this is important for not having errors, so probably should be near the top.

there are three different places where the python interpreter must be the same
major version (eg all 3.7). the tooling as it is now does not make that the
case by default - [TODO: make it so]

- the endpoint worker
- the endpoint
- the submitting user python env

TODO: make this consistent for a first time install experience: either describe
how to configure it in all three places, or make the defaults/documented
command lines make that happen.

The setup as I came to it is installing 3 different incompatible python version
without telling me not to.

## Port notes

nmap of amber.cqx.ltd.uk:

```
$ nmap amber.cqx.ltd.uk -p- -4

Starting Nmap 7.40 ( https://nmap.org ) at 2021-09-20 19:41 UTC
Nmap scan report for amber.cqx.ltd.uk (65.108.55.218)
Host is up (0.055s latency).
Other addresses for amber.cqx.ltd.uk (not scanned): 2a01:4f9:c010:e030::1
Not shown: 65522 closed ports
PORT      STATE SERVICE
22/tcp    open  ssh
2379/tcp  open  etcd-client
2380/tcp  open  etcd-server
6000/tcp  open  X11
8000/tcp  open  http-alt
8080/tcp  open  http-proxy
8443/tcp  open  https-alt
10249/tcp open  unknown
10250/tcp open  unknown
10256/tcp open  unknown
55001/tcp open  unknown
55002/tcp open  unknown
55003/tcp open  unknown

```

The above notes have two ports forwarded manually using kubectl port forwarding each time.

funcx-forwarder is configured to expose a number of ports, 55002-55005.

but in its environment, it declares these: which don't quite align.
it declares these:
      TASKS_PORT:                    55001
      RESULTS_PORT:                  55002
      COMMANDS_PORT:                 55003
as well as 8080

As far as remote nmap is concerned, 55001-3 are exposed, not -4 and -5.

So what's the configuration divergence here? (is there unnecessary configuration of those
ports, seeing as 55001 is finding its way in there anyway?)

the funcx-forwarder service lists 55001, 55003, 55005
which is a *third* combination of those different ports. (!)
they're labelled in the service as zmq1, zmq2, zmq3

... is the forwarder running in some weird non-kubernetes network env? (eg the host native network env?)  it appears to have an IP: field described in the pod:
IP:           65.108.55.218
IPs:
  IP:           65.108.55.218

and the chart has "hostNetwork: true"
 - so all the port forwards that its doing in the 55000...whatever range are unneeded I guess and thats why it doesn't matter that they're messed up?

[TODO: understand and rationalise that configuration. if this is always host network,
are any of those other port descriptions necessary at all? not in the minikube case
I think, but what about in real deployment]

what do the ports: declarations do in  funcx/templates/forwarder-deployment.yaml anyway?
it looks like they're explicitly adding on 1 to the actual values ??

These ports look like harmless fluff that is intellectually taxing/wasteful on someone
trying to understand... is that true?

Who is communicating with the forwarder?


TODO: If these ports can be configured publicly, can the ports for the web service
and websockets service also be configured that way?  What's the difference between
the web(sockets) ports and the forwarder ports?  On the production system are they
made fully public in different ways?



### nice ways to get endpoint in k8s cluster ofr devs

eg make it consistent every time over restarts rather than random each time?

or output it somewhere that cna be read programmatically by clients?

TODO: best common practice is probably to generate an endpoint ID and hard
configure it right from the start, as suggested by ryan. That eliminates the
need for fiddling in the logs to discover the random endpoint ID each time.
Be very clear that this needs to be unique.


## web-service build (and check others?) has a requiremenets.txt which
installs from git funcx api main

docker build doesn't invalidate the cache as the api main tag advances,
becaues the command is not changed, and so rebuilds are not built with the
latest main.

this is terrible and obscure and i only noticed it randomly in passing.

===
> docker build --no-cache -t funcx-web-service  is my default
￼
says yadu.
 - this has gone into the helm-chart Makefile documentation already
===

===
microk8s ingres (with ingress PR applied...)
install microk8s ingress. this puts in a DaemonSet that launches the ingress controller.
this needs editing:

root@pearl:~# microk8s kubectl get daemonset -n ingress
NAME                                DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR   AGE
nginx-ingress-microk8s-controller   1         1         1       1            1           <none>          12d

~/kubectl edit daemonset nginx-ingress-microk8s-controller  -n ingress

edit eg the container port (for @sirosen's use case, but not otherwise):
          ports:
          - containerPort: 80
            hostPort: 81
            name: http
            protocol: TCP
          - containerPort: 443
            hostPort: 443
            name: https
            protocol: TCP

and somewhere (perhaps the container args in that daemonset) remove the restriction on running 



===

# dockerfile endpoint in funcx vs python version
should force choice of python rather than defaulting to some rando version that
doesn't make sense:
--- a/Dockerfile-endpoint
+++ b/Dockerfile-endpoint
@@ -1,4 +1,5 @@
-ARG PYTHON_VERSION="3.8"
+ARG PYTHON_VERSION
+# eg PYTHON_VERSION="3.8"



# PRs and issues opened

https://github.com/funcx-faas/helm-chart/pull/36 (websockets installed from wrong tag)

https://github.com/funcx-faas/helm-chart/pull/39 (tidy up suggested values documentation)

https://github.com/funcx-faas/funcX/issues/600   (duplicate pod names - dupe of existing parsl issue)

https://github.com/funcx-faas/funcX/issues/601 (broken k8s worker pods accumulate forever)



## Making a release and deploying to the AWS clusters

The following is an incomplete guide to making and deploying a new release onto our development or production clusters.

Here are the components that need updating as part of a release, in the order they should be updated
due to dependencies. Note that only components that have changes for release need to updated and the
rest can safely be skipped:

* funcx-forwarder
    * Update version number
    * merge above changes to main in a PR
    * Create a branch off of main with the version number, for, eg: 'v0.3.3'.
      For dev releases, do alpha releases `v0.3.3a0`
    * Ensure that the branch has the CI tests passing and the publish step working

* funcx-web-service
    * Same steps as funcx-forwarder

* funcx-websocket-service
    * Same steps as funcx-websocket-service

* Update helm-charts
    * Update the smoke-tests in the helm-charts to use the new version numbers in `conftest.py`

* Prepare to deploy to cluster.
    * Confirm that all the bits to be deployed should be available on dockerhub.
    * Run `kubectl config current-context` which should return something like:

    >> arn:aws:eks:us-east-1:512084481048:cluster/funcx-dev

    * Make sure the right cluster is pointed to by kubectl, and use this terminal for all following steps.

* Download the current values deployed to the target cluster as a backup. Note: you can use this as a base values.yaml.
    >> helm get values funcx > enviornment.yaml

* Update the values to use the release branchnames as the new tags

* Deploy with:
    >> helm upgrade -f prod-values.yaml funcx funcx

> :warning: It is preferable to upgrade rather than blow away the current deployment and redeploy
    because, wiping the current deployment loses state that ties the Route53 entries to point at
    the ALB, and any configuration on the ALB itself could be lost.

> :warning: If the deployment was wiped here are the steps:
    * Go to Route53 on AWS Console and select the hosted zone: `dev.funcx.org`. Select the
      appropriate A record for the deployment you are updating and edit the record to update the
      value to something like `dualstack.k8s-default-funcxfun-dd14845f35-608065658.us-east-1.elb.amazonaws.com.`
    * Add the ALB to the existing WAF Rules here: `https://console.aws.amazon.com/wafv2/homev2/web-acl/funcx-prod-web-acl/d82023f9-2cd8-4aed-b8e3-460dd399f4b0/overview?region=us-east-1#`


* While a new forwarder will be launched on upgrade, the new one will not go online
  since it requires the ports that are in use by the older one. So you must manually
  delete the older funcx-forwarder pod.

  >> kubectl get pods
  \# Find the older funcx-forwarder pod

  >> kubctl delete pods \<NAME_OF_THE_OLDER_FUNCX_FORWARDER\>


## Deploy a temporary k8s deployment in the dev cluster

It is occasionally useful to deploy a full FuncX stack in the dev cluster under
a different namespace.  This is useful when two developers are both working on
or debugging a feature as well as to verify a feature works as expected before
potentially deploying to the main dev environment deployment.  These
instructions will get a second FuncX deployment (with k8s based redis,
postgres, and rabbitmq) running at a specified host under `*.api.dev.funcx.org`.

* To avoid forwarder port conflicts, ensure at least as many nodes are running 
  in EKS as there will be forwarder deployments since forwarders rely on host
  ports to be addressable.  To scale the node group you can use `eksctl scale
  nodegroup --cluster=funcx-dev --name=funcx-dev-node-group --nodes=2
  --nodes-max=2` where `nodes-max` and `nodes` are set to as many as are needed.
* Create a new namespace for your deployment: e.g. `kubectl create namespace josh-funcx` 
* Create a `values.yaml` that includes information about the host name to use 
  in the ingress definition.  E.g.:
    ingress:
      enabled: true
      host: josh-test.dev.funcx.org
      name: dev-lb
      subnets: subnet-0c0d6b32bb57c39b2, subnet-0906da1c44cbe3b8d
      use_alb: true
* Install the helm chart as described above, but specifying the new `values.yaml` file 
  and the namespace. E.g.: `helm install -f deployed_values/values.yaml josh-funcx funcx --namespace`
* Create a new route53 record for the given host (josh-test.dev.funcx.org).  
  We won't have to do this after [external dns](https://kubernetes-sigs.github.io/aws-load-balancer-controller/v2.2/guide/integrations/external_dns/) has been enabled.


## Advanced option: Deploying funcx-endpoint outside of K8s [this is "advanced" - move to end of doc, and crossref with other "install an endpoint" document]

The above noteis installed a funcx endpoint inside kubernetes, alongside the funcx services.
In real life, end users would install funcx endpoints elsewhere (on their compute
resources) and attach them to the officially funcx services.

It is also possible to install an endpoint elsewhere and attach it to services
deployed by this chart for dev purposes.

---
**NOTE**

This only works on Linux systems.

---

Here are the steps to install, preferably into your active conda environment:

```shell script
git clone https://github.com/funcx-faas/funcX.git
cd funcX
git checkout main
pip install funcx_sdk
pip install funcx_endpoint
```

Next create an endpoint configuration:

```shell script
funcx-endpoint
```

Update the endpoint's configuration file to point the endpoint to locally
deployed services, which we will setup in the next sections. If using default
values, the funcx_service_address should be set to http://localhost:5000/v2.

`~/.funcx/default/config.py`

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



## See also

More notes in the local_dev/ subdirectory that should be merged into this file

