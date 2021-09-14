import random


def double(x):
    return x * 2


def test_executor_basic(fx, fxc_args):
    """ Test executor interface
    """

    endpoint = fxc_args['tutorial_endpoint']
    x = random.randint(0, 100)
    fut = fx.submit(double, x, endpoint_id=endpoint)

    assert fut.result(timeout=10) == x * 2, "Got wrong answer"
