import pytest
from funcx import FuncXClient
from funcx.sdk.executor import FuncXExecutor

config = {
    # By default tests are against production
    "funcx_service_address": "https://api2.funcx.org/v2",
    "endpoint_uuid": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "results_ws_uri": "wss://api2.funcx.org/ws/v2/",
    "forwarder_version": "0.3.2",
    "api_version": "0.3.2",  # Version of funcx-web-service
    "funcx_version": "0.3.2",  # Version of funcx-web-service
    # This fn is public and searchable
    "public_hello_fn_uuid": "b0a5d1a0-2b22-4381-b899-ba73321e41e0",
    # Public tutorial endpoint
    "tutorial_endpoint": "4b116d3c-1703-4f8f-9f6f-39921e5864df",
}


def pytest_addoption(parser):
    """Add funcx-specific command-line options to pytest."""
    parser.addoption(
        "--endpoint",
        action="store",
        metavar="endpoint",
        nargs=1,
        default=[config["endpoint_uuid"]],
        help="Specify an active endpoint UUID",
    )

    parser.addoption(
        "--service-address",
        action="store",
        metavar="service-address",
        nargs=1,
        default=[config["funcx_service_address"]],
        help="Specify a funcX service address",
    )

    parser.addoption(
        "--ws-uri",
        action="store",
        metavar="ws-uri",
        nargs=1,
        default=[config["results_ws_uri"]],
        help="WebSocket URI to get task results",
    )


@pytest.fixture(scope="session")
def fxc_args(pytestconfig):
    fxc_args = {
        "funcx_service_address": pytestconfig.getoption("--service-address")[0],
        "results_ws_uri": pytestconfig.getoption("--ws-uri")[0],
    }
    fxc_args.update(config)
    return fxc_args


@pytest.fixture(scope="session")
def fxc(fxc_args):
    fxc = FuncXClient(**fxc_args)
    return fxc


@pytest.fixture(scope="session")
def async_fxc(fxc_args):
    fxc = FuncXClient(**fxc_args, asynchronous=True)
    return fxc


@pytest.fixture(scope="session")
def fx(fxc):
    fx = FuncXExecutor(fxc)
    return fx


@pytest.fixture(scope="session")
def endpoint(pytestconfig):
    endpoint = pytestconfig.getoption("--endpoint")[0]
    return endpoint
