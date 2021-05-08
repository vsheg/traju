"""Console script for traju."""

from os import cpu_count
import sys
from argparse import ArgumentParser, Namespace

import logging
from pathlib import Path
from typing import *

from .helpers import *


logger = logging.getLogger(__name__)


def parse_args() -> Namespace:
    '''Parse command line arguments.'''

    parser = ArgumentParser(prog='traju', description='Proceed arguments')
    add_arg = parser.add_argument  # alias

    # File parameters
    add_arg(
        'path',
        help='path to directory or to trajectories',
        type=Path,
        nargs='*',
        default=Path(),
    )
    add_arg('--recursive', '-r', help='go through subfolders', action='store_true')
    add_arg(
        '--strict',
        help='stop when a problem occurs, else just warn',
        action='store_true',
    )
    add_arg('--traj-exts', help='trajectory file extentions', type=str, default='nc')
    add_arg('--top-exts', help='topology file extentions', type=str, default='prmtop')
    add_arg(
        '-y',
        '--yes',
        help='run script sliently without interactivity',
        action='store_true',
    )
    add_arg(
        '--summary',
        '-s',
        help='write summary file for joined trajectories',
        action='store_true',
    )

    # Computation parameters
    add_arg(
        '--max-procs',
        '-p',
        help='upper limit for number of using processes '
        '(note: the number of CPU cores is upper limit too)',
        type=int,
        default=16,
    )

    # Mutually exclusive output options
    save_group = parser.add_mutually_exclusive_group()
    save_group.add_argument(
        '--overwrite', '-o', help='overwrite original files', action='store_true'
    )
    save_group.add_argument(
        '--nearby',
        '-n',
        help='write new trajctory to the same folder as the original',
        action='store_true',
    )
    save_group.add_argument(
        '--join', '-j', help='join trajectories into one', action='store_true'
    )

    # cpptraj  parameters
    add_arg('--prefix', help='add prefix to new trajectories', type=str, default='')
    add_arg('--postfix', help='add postfix to new trajectories', type=str, default='_u')
    add_arg(
        '--ext', '-e', help='extension for new trajectories', type=str, default='nc'
    ),
    add_arg(
        '--align',
        '-a',
        help='align protein backbone to the first frame',
        action='store_true',
    ),
    add_arg('--dehyd', '-d', help='remove water', action='store_true')

    # proceed arguments

    args = parser.parse_args()
    logger.debug('Arguments were parsed')
    return args


args = parse_args()

#
PATHS: Sequence[Path] = vector_like(args.path)  # paths of trajectories
logger.debug('Number of provided paths: %s', len(PATHS))

# Interface flags
SILENT: bool = not args.yes  # don't get user approval
if SILENT:
    logging.getLogger().setLevel(logging.WARN)  # change level of root logger
STRICT: bool = args.strict  # stop if something went wrong at least with one traj

# Computing parameters
MAX_PROCS: int = args.max_procs

# Saving flags
NEARBY: bool = args.nearby  # save out trajs in the same folder
JOIN: bool = args.join  # join input trajs into one
OVERWRITE: bool = args.overwrite  # replace original trajs with outs

# File naming
TOP_EXTENTIONS: Iterable[str] = vector_like(args.top_exts)  # without preceding dot
TRAJ_EXTENTIONS: Iterable[str] = vector_like(args.traj_exts)  # too
PREFIX: str = args.prefix
POSTFIX: str = args.postfix
TRAJ_OUT_EXT: str = args.ext

#
DEHYDRATE: bool = args.dehyd
ALIGN: bool = args.align


def find_trajs(PATHS: Iterable) -> Sequence[Path]:
    '''Collect specified trajs into list and find it in provided directories.'''

    dirs, trajs = apart(lambda path: path.is_file(), PATHS)
    trajs = list(trajs)  # to make sure

    if trajs:
        logger.info('%s traj(s) specified explicitly', len(trajs))
        if not SILENT:
            for traj in trajs:
                print(f'* {traj}')

    # find trajs in provided folders
    if dirs:
        add_trajs = []
        for dir_ in dirs:
            for ext in args.traj_exts:
                for path in dir_.glob(('**/*.' if args.recursive else '*.') + ext):
                    if path.is_file():
                        add_trajs.append(path)
        logger.info(
            '%s traj(s) found in folder'
            + (' and subfolders recursively' if args.recursive else ''),
            len(add_trajs),
        )

        if not SILENT:
            for traj in add_trajs:
                print(f' * {traj}')

        trajs.extend(add_trajs)

    return trajs


TRAJS = find_trajs(PATHS)


def main():
    '''CLI entry point.'''

    from .traju import TASKS, proceed_tasks

    proceed_tasks(TASKS)
    return 0


if __name__ == '__main__':
    sys.exit(main())  # pragma: no cover
