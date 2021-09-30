import json
import os

import pytest
from funcx import FuncXClient
from funcx.sdk.executor import FuncXExecutor

# the non-tutorial endpoint will be required, with the following priority order for
# finding the ID:
#
#  1. `--endpoint` opt
#  2. FUNX_LOCAL_ENDPOINT_ID (seen here)
#  3. FUNX_LOCAL_ENDPOINT_NAME (the name of a dir in `~/.funcx/`)
#  4. An endpoint ID found in ~/.funcx/default/endpoint.json
#
#  this var starts with the ID env var load
_LOCAL_ENDPOINT_ID = os.getenv("FUNCX_LOCAL_ENDPOINT_ID")

_CONFIGS = [
    {
        "config_name": "PROD",
        # By default tests are against production, which means we do not need to pass
        # any arguments to the client object (default will point at prod stack)
        "client_args": {},
        # assert versions are as expected on prod
        "forwarder_version": "0.3.2",
        "api_version": "0.3.2",
        "funcx_version": "0.3.2",
        # This fn is public and searchable
        "public_hello_fn_uuid": "b0a5d1a0-2b22-4381-b899-ba73321e41e0",
        # Public tutorial endpoint
        "tutorial_endpoint": "4b116d3c-1703-4f8f-9f6f-39921e5864df",
        # other endpoint to test
        "endpoint_uuid": _LOCAL_ENDPOINT_ID,
    },
    {
        "config_name": "LOCAL",
        # localhost; typical defaults for a helm deploy
        "client_args": {
            "funcx_service_address": "http://localhost:5000/v2",
            "results_ws_uri": "ws://localhost:6000/ws/v2/",
        },
        "endpoint_uuid": _LOCAL_ENDPOINT_ID,
    },
]


def _get_config(name):
    return next(x for x in _CONFIGS if x["config_name"] == name)


def _get_local_endpoint_id():
    # get the ID of a local endpoint, by name
    # this is only called if
    #  - there is no endpoint in the config (e.g. config via env var)
    #  - `--endpoint` is not passed
    local_endpoint_name = os.getenv("FUNCX_LOCAL_ENDPOINT_NAME", "default")
    data_path = os.path.join(
        os.path.expanduser("~"), ".funcx", local_endpoint_name, "endpoint.json"
    )
    with open(data_path) as fp:
        data = json.load(fp)
    return data["endpoint_id"]


def pytest_addoption(parser):
    """Add funcx-specific command-line options to pytest."""
    parser.addoption(
        "--funcx-local",
        action="store_true",
        default=False,
        help="Use local testing config",
    )
    parser.addoption(
        "--endpoint", metavar="endpoint", help="Specify an active endpoint UUID"
    )
    parser.addoption(
        "--service-address",
        metavar="service-address",
        help="Specify a funcX service address",
    )
    parser.addoption(
        "--ws-uri", metavar="ws-uri", help="WebSocket URI to get task results"
    )


@pytest.fixture(scope="session")
def funcx_test_config(pytestconfig):
    # start with basic config load
    config = _get_config("PROD")
    if pytestconfig.getoption("--funcx-local"):
        config = _get_config("LOCAL")

    # if `--endpoint` was passed or `endpoint_uuid` is present in config,
    # handle those cases
    endpoint = pytestconfig.getoption("--endpoint")
    if endpoint:
        config["endpoint_uuid"] = endpoint
    elif config["endpoint_uuid"] is None:
        config["endpoint_uuid"] = _get_local_endpoint_id()

    # set URIs if passed
    client_args = config["client_args"]
    ws_uri = pytestconfig.getoption("--ws-uri")
    api_uri = pytestconfig.getoption("--service-address")
    if ws_uri:
        client_args["results_ws_uri"] = ws_uri
    if api_uri:
        client_args["funcx_service_address"] = api_uri

    return config


@pytest.fixture(scope="session")
def fxc(funcx_test_config):
    client_args = funcx_test_config["client_args"]
    fxc = FuncXClient(**client_args)
    return fxc


@pytest.fixture(scope="session")
def async_fxc(funcx_test_config):
    client_args = funcx_test_config["client_args"]
    fxc = FuncXClient(**client_args, asynchronous=True)
    return fxc


@pytest.fixture(scope="session")
def fx(fxc):
    fx = FuncXExecutor(fxc)
    return fx


@pytest.fixture
def endpoint(funcx_test_config):
    return funcx_test_config["endpoint_uuid"]


@pytest.fixture
def _tutorial_endpoint(funcx_test_config):
    return funcx_test_config.get("tutorial_endpoint")


@pytest.fixture
def tutorial_endpoint(_tutorial_endpoint):
    if not _tutorial_endpoint:
        pytest.skip("test requires the tutorial_endpoint")
    return _tutorial_endpoint


@pytest.fixture
def tutorial_funcion_id(funcx_test_config):
    funcid = funcx_test_config.get("public_hello_fn_uuid")
    if not funcid:
        pytest.skip("test requires the tutorial function")
    return funcid


@pytest.fixture
def try_tutorial_endpoint(_tutorial_endpoint, endpoint):
    # a variant of the tutorial_endpoint fixture which failsover to the
    # non-tutorial endpoint if the tests are running locally, rather than skipping
    if _tutorial_endpoint:
        return _tutorial_endpoint
    return endpoint
