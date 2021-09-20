# helm-chart
Helm Chart for Deploying funcX stack

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![NSF-2004894](https://img.shields.io/badge/NSF-2004894-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=2004894)
[![NSF-2004932](https://img.shields.io/badge/NSF-2004932-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=2004932)

This application includes:
* FuncX Web-Service
* FuncX Websocket Service
* FuncX Forwarder
* Kubernetes endpoint
* Postgres database
* Redis Shared Data Structure
* RabbitMQ broker

## benc notes on what i added onto a hetzner machine installed with ubuntu 20.04.03 - as root (because this is a VM dedicated to this project, so I don't care about user permissions for kubernetes level stuff)


apt-get install docker.io
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
install minikube-linux-amd64 /usr/local/bin/minikube

apt-get install contrack   # because: ❌  Exiting due to GUEST_MISSING_CONNTRACK: Sorry, Kubernetes 1.22.1 requires conntrack to be installed in root's path

minikube --driver=none    # because i am root in a VM. otherwise apparently driver=docker might be nice? I haven't tried

Now can run to see running pods

$ minikube kubectl -- get pods -A

This gives me 7 runnings k8s pods.


now install helm, following debian/apt instructions here: 
https://helm.sh/docs/intro/install/

curl https://baltocdn.com/helm/signing.asc | sudo apt-key add -
sudo apt-get install apt-transport-https --yes
echo "deb https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm

now can run:

# helm

and see the default helm help text.

now get the funcx helm repo:

mkdir src
cd  src
git clone git@github.com:funcx-faas/helm-chart
cd helm-chart

and run the first helm command from below:

helm dependency update funcx

which will download some stuff.

Note that it downloads a funcx_endpoint chart over http - that isn't something contained in this repo, even though it is a funcx related chart...

see notes further down for continuation...

## Preliminaries

how is this a preliminary rather than part of the main install? it even looks like a funcx-endpoint is set up as part of helm automatically ... so is this whole endpoint section irrelevant for an initial install? or at least, there should be better intro description at this point
that an endpoint will be deployed inside k8s?

make a decision for the user - as they are new. they can try different ways later, which
can be documented elsewhere - for example, this is the helm repo so should be talking
about the helm deployment of the endpoint. Or pointing people at the endpoint repo.

There are two modes in which funcx-endpoints could be deployed: 


1. funcx-endpoint deployed outside k8s, connecting to hosted services in k8s
2. funcx-endpoint deployed inside k8s

Also be clear on the deployment modes: production-like (eg with many users, centrally,
with expection that images are from tags, endpoints deployed by other people) 
and development-like - eg on my own private VM with my own hacked up source changes and
all sorts of mess, and everything including endpoints deployed by me.

be clear throughout this document what refers to those two use cases.

### Deploying funcx-endpoint outside of K8s

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


### Deploying funcx-endpoint into the K8s deployment

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

## Installing FuncX

[how does this section relate to the previous section? I think the
]

1. Make a clone of this repository
2. Download subcharts:
    ```shell script
     helm dependency update funcx
    ```
3. Create your own `values.yaml` inside the Git ignored directory `deployed_values/`
     [forward reference to the two different values sections later on in this
      document: should I just have the three lines mentioned here? or should I
      be copy-pasting a huge example?]
4. Obtain Globus Client ID and Secret. These secrets need to exist in the
   correct Globus Auth app. Ask for access to the credentials by contacting
   https://github.com/BenGalewsky or sending a message to the `dev` funcx Slack
   channel. Once you have your credentials, paste them into your `values.yaml`:
    ```yaml
    webService:
      globusClient: <<your app client>>
      globusKey: <<your app secret>>
    ```
5. Install the helm chart:
    ```shell script
    helm install -f deployed_values/values.yaml funcx funcx
    ```
6. You can access your web service through the ingress or via a port forward
to the web service pod. Instructions are provided in the displayed notes.
[what ingress? there is no ingress resource created by helm? talking about the
'service' resource for these?] 

now i see a bunch of services including a funcx endpoint

looks like this:

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



7. You should be able to see the endpoint registering with the web service
in their respective logs, along with the forwarder log. Check the endpoint's
logs for its ID. 

[clarify which logs / *where* those logs are? explicitly which (3?) logs to
look at... - who is registering with whom?]

Endpoint log will look like:

2021-09-14 16:36:02 endpoint.endpoint_manager:172 [INFO]  Starting endpoint with uuid: cfd389f3-4eda-413b-af95-4d54a8e944dc

forwarder will look like:
{"asctime": "2021-09-14 18:20:44,535", "name": "funcx_forwarder.forwarder", "levelname": "DEBUG", "message": "endpoint_status_message", "log_type": "endpoint_status_message", "endpoint_id": "cfd389f3-4eda-413b-af95-4d54a8e944dc", "endpoint_status_message": {"_payload": null, "_header": "b'\\xcf\\xd3\\x89\\xf3N\\xdaA;\\xaf\\x95MT\\xa8\\xe9D\\xdc'", "ep_status": {"task_id": -2, "info": {"total_cores": 0, "total_mem": 0, "new_core_hrs": 0, "total_core_hrs": 0, "managers": 0, "active_managers": 0, "total_workers": 0, "idle_workers": 0, "pending_tasks": 0, "outstanding_tasks": {}, "worker_mode": "no_container", "scheduler_mode": "hard", "scaling_enabled": true, "mem_per_worker": null, "cores_per_worker": 1.0, "prefetch_capacity": 10, "max_blocks": 100, "min_blocks": 1, "max_workers_per_node": 1, "nodes_per_block": 1}}, "task_statuses": {}}}

web service will look like:
{"asctime": "2021-09-14 16:36:03,273", "name": "funcx_web_service", "levelname": "INFO", "message": "Successfully registered cfd389f3-4eda-413b-af95-4d54a8e944dc in database"}

### connecting clients

the startup message (from helm) has a couple of kubectl port-forward commands that might be a bit wrong - i ended up using these two:
# minikube kubectl -- port-forward --address 0.0.0.0 service/funcx-funcx-web-service 8000
# minikube kubectl -- port-forward --address 0.0.0.0 service/funcx-funcx-websocket-service 6000

These port forwards are only temporary - they run as foreground processes and break as soon as the pods change (for example due to restarts). That seems a bit frustrating if they're meant to be pointing to services. Is there a more persistent kubernetes configuration that can be used to expose to the world? And for other people, to expose to whatever their security-scoped environment is?

This will expose the services on port 8000 and port 6000  - because this is a service, the 2nd port number in the helm suggested text is ignored, I think - so that could be removed in a PR (as long as I check and justify that with documentation links)

now from a working funcx install, create a funcx client pointed at the current 
service, like this:

fxc = FuncXClient(funcx_service_address="http://amber.cqx.ltd.uk:8000/v2")

and then run quickstart guide style stuff - probably i don't need to paste it here, but
I could...


from funcx.sdk.client import FuncXClient

fxc = FuncXClient(PARMS HERE)

def hello_world():
  return "Hello World!"

func_uuid = fxc.register_function(hello_world)

tutorial_endpoint = 'LOCAL ENDPOINT HERE'
result = fxc.run(endpoint_id=tutorial_endpoint, function_id=func_uuid)

print(fxc.get_result(result))

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
  workerImage: python:3.8-buster
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


## Values

> :warning: **USE THE FOLLOWING deployed_values/values.yaml** Omit the
> funcx_endpoint section if using an externally deployed endpoint.

should I use the following values.yaml or the values.yaml I was told to make earlier?
dedupe - and if this section is the values.yaml i should be using, move it up to
where i am told to create the values.yaml

eg. why do I need to be exposing postgres to the internet?

``` yaml
webService:
  pullPolicy: Always
  globusClient: <GLOBUS_CLIENT_ID_STRING>
  globusKey: <GLOBUS_CLIENT_KEY_STRING>
  tag: main

websocketService:
  pullPolicy: Always
  tag: main

# Note that we install numpy into the worker so that we can run tests against the local 
# deployment
# Note that the workerImage needs the same python version as is used in the funcx_endpoint 
# image. This requirement will be relaxed [give an issue url for tracking this or remove the promise/dream. it is barely relevant to config docs]
funcx_endpoint:
  enabled: true
  funcXServiceAddress: http://funcx-funcx-web-service:8000
  image:
    pullPolicy: Always
    tag: main
  maxBlocks: 2
  initBlocks: 0
  minBlocks: 2
  workerInit: pip install funcx-endpoint==0.3.2 numpy
  workerImage: python:3.7-buster

forwarder:
  enabled: true
  tag: main
  pullPolicy: Always

redis:
  master:
    service:
      nodePort: 30379
      type: NodePort

postgresql:
  service:
    nodePort: 30432
    type: NodePort

rabbitmq:
  auth:
    erlangCookie: c00kie
  pullPolicy: Always
```

### Additional config
[are these values that are defaulted in funcx/values.yaml and can be overridden in
deployed_values/values.yaml?]

There are a few values that can be set to adjust the deployed system
configuration

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


## Sealed Secrets
[why would i want to do this?]
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

## Subcharts
This chart uses two subcharts to supply dependent services. You can update
settings for these by referencing the subchart name and values from
their READMEs.

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



how can i run a test job against this install?

# upgrades
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


funcx endpoint worker pods lose their logs at each restart - which is awkward to examine when the logs are in an every-two-minutes restart loop due to missing heartbeat. [should they even be autorestarting in that situation, rather than letting the endpoint handle restarting them if it still wants them?]


## Upgrading and developing against non-main environments

i've been trying this but it's not clear that it is pulling down the latest of
everything: (I think it does, but just the images are not changing often
upstream from me?)
 helm upgrade -f deployed_values/values.yaml funcx funcx --recreate-pods

