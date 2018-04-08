import asyncio
from concurrent.futures import ALL_COMPLETED
from concurrent.futures import FIRST_COMPLETED
from typing import Awaitable
from typing import List
from typing import TypeVar


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
            tasks, timeout=1, return_when=ALL_COMPLETED,
        )
        while len(pending) >= n:
            done, pending = await asyncio.wait(
                pending, return_when=FIRST_COMPLETED,
            )

    while pending:
        done, pending = await asyncio.wait(tasks, return_when=ALL_COMPLETED)

    return [t.result() for t in tasks]
