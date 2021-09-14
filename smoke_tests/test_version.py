import requests


def test_web_service(fxc, endpoint, fxc_args):
    """ This test checks 1) web-service is online, 2) version of the funcx-web-service
    """
    service_address = fxc.funcx_service_address

    response = requests.get(f"{service_address}/version")

    assert response.status_code == 200, f"Request to version expected status_code=200, got {response.status_code} instead"

    service_version = response.json()
    api_version = fxc_args['api_version']
    assert service_version == api_version, f"Expected API version:{api_version}, got {service_version}"


def test_forwarder(fxc, endpoint, fxc_args):
    """ This test checks 1) forwarder is online, 2) version of the forwarder
    """
    service_address = fxc.funcx_service_address

    response = requests.get(f"{service_address}/version", params={'service': 'all'})

    assert response.status_code == 200, f"Request to version expected status_code=200, got {response.status_code} instead"

    forwarder_version = response.json()["forwarder"]
    expected_version = fxc_args['forwarder_version']
    assert forwarder_version == expected_version, \
        f"Expected Forwarder version:{expected_version}, got {forwarder_version}"


def say_hello():
    return "Hello World!"


def test_simple_function(fxc):
    """ Test whether we can register a function
    """
    func_uuid = fxc.register_function(say_hello)
    assert func_uuid is not None, "Invalid function uuid returned"


def test_tutorial_ep_status(fxc, fxc_args):
    """ Test whether the tutorial EP is online and reporting status
    """
    response = fxc.get_endpoint_status(fxc_args["tutorial_endpoint"])

    assert response['status'] == "online", \
        f"Expected tutorial EP to be online, got:{response['status']}"
