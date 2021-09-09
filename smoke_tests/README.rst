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
* funcx_version

Running tests
-------------

* Install requirements:

     >> pip install -r requirements.txt

* Run tests:

     >> pytest .
