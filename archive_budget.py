"""Cooperative deadlines for resumable archive batches."""
from contextlib import contextmanager
from contextvars import ContextVar
import time

_deadline=ContextVar('archive_deadline',default=None)


class BatchDeadline(Exception):
    """Save the current checkpoint and continue in the next scheduled batch."""


def remaining():
    end=_deadline.get()
    return None if end is None else end-time.monotonic()


def check(reserve=45):
    left=remaining()
    if left is not None and left<=reserve:raise BatchDeadline('Batch time budget reached; draft retained for continuation')


def timeout(maximum,reserve=30):
    left=remaining()
    if left is None:return maximum
    if left<=reserve:raise BatchDeadline('Insufficient time for another operation')
    return min(maximum,left-reserve)


@contextmanager
def limit(seconds):
    prior=_deadline.get();end=time.monotonic()+max(0,seconds)
    token=_deadline.set(min(prior,end) if prior is not None else end)
    try:yield
    finally:_deadline.reset(token)
