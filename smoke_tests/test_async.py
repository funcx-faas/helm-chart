import random
import asyncio


def squared(x):
    return x ** 2


async def simple_task(fxc, endpoint):
    squared_function = fxc.register_function(squared)
    x = random.randint(0, 100)
    task = fxc.run(x, endpoint_id=endpoint, function_id=squared_function)
    result = await asyncio.wait_for(task, 20)
    assert result == squared(x), "Got wrong answer"


def test_simple(async_fxc, fxc_args):
    """ Testing basic async functionality
    """
    async_fxc.loop.run_until_complete(simple_task(async_fxc, fxc_args['tutorial_endpoint']))
