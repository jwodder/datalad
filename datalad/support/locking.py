from fasteners import (
    InterProcessLock,
    try_lock,
)
from contextlib import contextmanager

from .path import exists
from ..utils import unlink

import logging
lgr = logging.getLogger('datalad.locking')


def _get(entry):
    """A helper to get the value, be it a callable or callable with args, or value

    """
    if isinstance(entry, (tuple, list)):
        func, args = entry
        return func(*args)
    elif callable(entry):
        return entry()
    else:
        return entry


@contextmanager
def lock_if_check_fails(
    check,
    lock_path,
    operation=None,
    blocking=True,
    _return_acquired=False,
    **kwargs
):
    """A context manager to establish a lock conditionally on result of a check

    It is intended to be used as a lock for a specific file and/or operation,
    e.g. for `annex get`ing a file or extracting an archive, so only one process
    would be performing such an operation.

    If verification of the check fails, it tries to acquire the lock, but if
    that fails on the first try, it will rerun check before proceeding to func

    checker and lock_path_prefix could be a value, or callable, or
    a tuple composing callable and its args

    Unfortunately yoh did not find any way in Python 2 to have a context manager
    which just skips the entire block if some condition is met (in Python3 there
    is ExitStack which could potentially be used).  So we would need still to
    check in the block body if the context manager return value is not None.

    Note also that the used type of the lock (fasteners.InterprocessLock) works
    only across processes and would not lock within the same (threads) process.

    Parameters
    ----------
    check: callable or (callable, args) or value
      If value (possibly after calling a callable) evaluates to True, no
      lock is acquired, and no context is executed
    lock_path: callable or (callable, args) or value
      Provides a path for the lock file, composed from that path + '.lck'
      extension
    operation: str, optional
      If provided, would be part of the locking extension
    blocking: bool, optional
      If blocking, process would be blocked until acquired and verified that it
      was acquired after it gets the lock
    _return_acquired: bool, optional
      Return also if lock was acquired.  For "private" use within DataLad (tests),
      do not rely on it in 3rd party solutions.
    **kwargs
      Passed to `.acquire` of the fasteners.InterProcessLock

    Returns
    -------
    result of check, lock[, acquired]
    """
    check1 = _get(check)
    if check1:  # we are done - nothing to do
        yield check1, None
        return
    # acquire blocking lock
    lock_filename = _get(lock_path)

    lock_filename += '.'
    if operation:
        lock_filename += operation + '-'
    lock_filename += 'lck'

    lock = InterProcessLock(lock_filename)
    acquired = False
    try:
        lgr.debug("Acquiring a lock %s", lock_filename)
        acquired = lock.acquire(blocking=blocking, **kwargs)
        lgr.debug("Acquired? lock %s: %s", lock_filename, acquired)
        if blocking:
            assert acquired
        check2 = _get(check)
        ret_lock = None if check2 else lock
        if _return_acquired:
            yield check2, ret_lock, acquired
        else:
            yield check2, ret_lock
    finally:
        if acquired:
            lgr.debug("Releasing lock %s", lock_filename)
            lock.release()
            if exists(lock_filename):
                unlink(lock_filename)
