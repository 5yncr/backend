import asyncio
from concurrent.futures import ALL_COMPLETED
from concurrent.futures import FIRST_COMPLETED
from typing import Awaitable
from typing import List
from typing import TypeVar

from syncr_backend.util.log_util import get_logger


logger = get_logger(__name__)


R = TypeVar('R')


async def limit_gather(
    fs: List[Awaitable[R]], n: int, task_timeout: int=0,
) -> List[R]:
    """
    Gathers the tasks in fs, but only allows n at a time to be pending.
    If task_timeout is greater than 0, allows each task that long to complete
    before trying the next.

    Useful a large list of tasks need to be completed, but running too many may
    cause side effects (ie, sockets timing out).

    :param fs: A list of awaitable objects to run
    :param n: The maximum number to allow to be pending at a time
    :param task_timeout: Give each task this long before trying the next
    :return: A list of what is returned by the tasks in fs
    """
    tasks = []  # List[asyncio.Future[R]]

    for f in fs:
        tasks.append(asyncio.ensure_future(f))

        done, pending = await asyncio.wait(
            tasks, timeout=task_timeout, return_when=ALL_COMPLETED,
        )
        while len(pending) >= n:
            done, pending = await asyncio.wait(
                pending, return_when=FIRST_COMPLETED,
            )

    while pending:
        done, pending = await asyncio.wait(tasks, return_when=ALL_COMPLETED)

    return [t.result() for t in tasks]


async def process_queue_with_limit(
    queue: 'asyncio.Queue[Awaitable[R]]', n: int,
    done_queue: 'asyncio.Queue[R]', task_timeout: int=0,
):
    """Processses up to n tasks from queue at a time, putting the results in
    done_queue.

    Otherwise similar to limit_gather.

    This function does not return, and should be cancled when queue.join()
    returns, everything from done_queue has been processed, and there is
    nothing left to add.

    :param queue: The queue of input tasks
    :param n: The max number of pending tasks at a time
    :param done_queue: Queue to add results to
    :param task_timeout: Allow tasks to take up to this long before running
    another
    """
    tasks = []
    while True:
        task = asyncio.ensure_future(await queue.get())
        task.add_done_callback(
            lambda future: done_queue.put_nowait(future.result()),
        )
        task.add_done_callback(
            lambda _: queue.task_done(),
        )
        tasks.append(task)

        done, pending = await asyncio.wait(
            tasks, timeout=task_timeout, return_when=ALL_COMPLETED,
        )
        while len(pending) >= n:
            done, pending = await asyncio.wait(
                pending, return_when=FIRST_COMPLETED,
            )