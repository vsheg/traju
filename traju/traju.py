'''traju is a simple util for batch processing of MD trajectories using AmberTools'
cpptraj
'''
from __future__ import annotations

__all__ = []


from os import getenv
from sys import stdout
from shutil import move
from pathlib import Path

from typing import *
from itertools import chain
import logging

import asyncio as aio
from threading import Lock
from subprocess import Popen, PIPE
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

from uuid import uuid1

from .cli import (
    OVERWRITE,
    TOP_EXTENTIONS,
    TRAJ_EXTENTIONS,
    TRAJS,
    DEHYDRATE,
    ALIGN,
    TRAJ_OUT_EXT,
    NEARBY,
    JOIN,
    STRICT,
    PREFIX,
    POSTFIX,
    SILENT,
    MAX_PROCS,
)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stdout)  # print to console
logger.addHandler(handler)


def test_cpptraj():
    '''Test `cpptraj` is available'''
    with Popen('cpptraj', stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True) as proc:

        proc.communicate(input=b'quit')
        if proc.returncode == 127:
            msg = '`cpptraj` wasn\'t found'
            if not getenv('AMBERHOME'):
                msg += ', env `AMBERHOME` not assigned too'
            logger.error(msg)
        if proc.returncode != 0:
            raise SystemExit('Something went wrong, couldn\'t call `cpptraj`')
    logger.debug('`cpptraj` is available')


def cpptraj_inp(top: Path, traj: Path, out: Path) -> str:
    '''Generate input script for cpptraj'''

    s = f'''\
    parm {top}
    trajin {traj}
    {'strip :WAT' if DEHYDRATE else ''}
    {'align :3-999999&@CA,C,O,N,H' if ALIGN else ''} #TODO: edit end index and document backbone atoms
    trajout {out}
    run
    '''
    return s


def tmp_filename() -> str:
    '''Return unique pseudo-random filename'''
    return str(uuid1()) + TRAJ_OUT_EXT


def proceed(top: Path, traj: Path, out: Path) -> Path:
    '''Run script on single trajectory'''

    tmp = out_filename(traj, stem=tmp_filename())  # in user's working directory

    if NEARBY:
        out = traj.parent / out

    with Popen('cpptraj', stdin=PIPE, stdout=PIPE) as proc:
        inp = cpptraj_inp(top, traj, tmp)
        inp = inp.encode()
        proc.communicate(input=inp)
        proc.wait()

        global COUNTER
        with lock:
            COUNTER += 1

        if proc.returncode == 0:
            if OVERWRITE:
                move(tmp, traj)  # thread safe on UNIXб unlike Path.rename (?)
            else:
                move(tmp, out)  # see above
        else:
            logger.error('Processing of `%s` returns non-zero exit code', traj)
            tmp.unlink()
            logger.error('Suspicious tmp out traj file `%s` was deleted', tmp)

            if STRICT:
                logger.warn('Execution stopped: `--strict` was specified')
                raise SystemExit()

    return out


def proceed_all(top: Path, trajs: Iterable[Path]) -> list[Path]:
    '''Run script to combine all trajectories into one file'''
    pass
    return list()


# preparation for trajs processing

logger.debug('Starting to create %s task(s)', len(TRAJS))


def find_topology(traj: Path) -> Optional[Path]:
    ''' '''
    folder = traj.parent
    top = (folder.glob('*' + ext) for ext in TOP_EXTENTIONS)
    top = list(chain(*top))

    if len(top) == 0:
        logger.warning('No topology file found for %s traj', folder, traj)
        return
    elif (l := len(top)) > 1:
        logger.warning('%s topology files found in `%s`', l, folder)
        return

    return top[0]


def out_filename(traj: Path, stem: Optional[str] = None) -> Path:
    ''' '''
    ext = TRAJ_OUT_EXT if TRAJ_OUT_EXT else traj.suffix
    stem = stem or traj.stem
    path = Path(TRAJ_OUT_EXT + stem + POSTFIX + '.' + ext)
    return path  # TODO: warn if bad ext


TASKS: list[tuple[Path, Path, Path]] = []  # container for tasks

for traj in TRAJS:
    if not (top := find_topology(traj)):
        if STRICT:
            raise SystemExit()
        else:
            break

    # TODO: incaplulate `if` to function not to check for all trajs
    if NEARBY:
        out = traj.parent / out_filename(traj)
    elif OVERWRITE:
        out = traj
    else:
        out = out_filename(traj)

    TASKS.append((top, traj, out))


def all_unique(it: Iterable[Path]) -> bool:
    '''Checks that all elements in collection is unique'''
    s = set()
    for el in it:
        if el in s:
            return False
        s.add(el)
    return True


if not all_unique(out for _, _, out in TASKS):
    logger.warning(
        'Non-unique names for trajectories were found, '
        'outputs will be overwritten! '
        'Note: use can you --nearby/-n to avoid this'
    )
    raise SystemError()

# Getting the user's approval

if not SILENT:
    print('Do you want to proceed? (y/n):', end=' ')

    for attempt in range(3):
        responce = input().strip().lower()
        if responce == 'y':
            logger.debug('Approval to start has been received')
            break
        elif responce == 'n':
            logger.debug('User didn\'t want to procced')
            raise SystemExit()
        else:
            print('Try again (y/n):', end=' ')
    else:
        logger.debug('User approval to start can\'t be interpreted')
        raise SystemExit('It was not clear')

# Parallel processing

lock = Lock()  # used for counter
COUNTER = 0  # global counter variable
N_TASKS = len(TASKS)


async def status():
    '''Prints trajs processing status while executing.'''
    while True:
        print(f'{COUNTER}/{N_TASKS}', end='\r')
        if COUNTER >= N_TASKS:
            break
        await aio.sleep(0.1)
    print()


SUBPROCESS_COUNT: int = min(MAX_PROCS, cpu_count())


def proceed_tasks(TASKS: list[tuple]):
    test_cpptraj()
    with ThreadPool(SUBPROCESS_COUNT) as pool:
        logger.debug('%s thread(s) allocated for trajs processing', SUBPROCESS_COUNT)
        pool.starmap_async(proceed, TASKS)
        aio.run(status())
