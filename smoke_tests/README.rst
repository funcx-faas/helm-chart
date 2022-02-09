Smoke Tests
===========

These tests are designed to quickly run some sanity checks on a deployment.
The goals of these tests are to:
* Quickly identify faults
* Ensure that **all** components deployed correctly with the right versions

How-to
------

These test have to be updated for each deployment, with updates to the `conftest.py`.
Here are the config options that **must** be updated per release:

* forwarder_version
* api_version

Running tests
-------------

* Install requirements:

     >> pip install -r requirements.txt

* Run tests:

     >> pytest .

Running Against Local K8s
-------------------------

To run against your local cluster, the default configuration will usually work.
Use

.. code-block:: bash

    pytest . --funcx-local

Or, from the repo root, invoke this with

.. code-block:: bash

    make test-local

By default, this will look for a local endpoint ID in several locations. If no
options are set, it uses the ID found in `~/.funcx/default/endpoint.json`.

You can configure it to use a different local endpoint name (not `default`) by
setting the `FUNCX_LOCAL_ENDPOINT_NAME` env var.

Additional ways of settings the endpoint ID to use are:

- set `FUNCX_LOCAL_ENDPOINT_ID` (higher precedence than `~/.funcx/` dir)

- pass the `--endpoint <UUID>` option to `pytest` (highest precedence)

All tests should pass when run locally. Tests which cannot work on a local
stack are marked with `pytest.skip` and will be skipped.
