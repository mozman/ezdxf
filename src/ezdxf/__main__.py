#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import sys
import argparse
from pathlib import Path
from ezdxf import __version__, options
from ezdxf.acc import USE_C_EXT
from ezdxf import commands
from ezdxf.tools import fonts

YES_NO = {True: 'yes', False: 'no'}
options.load_proxy_graphics = True


def add_common_arguments(parser):
    parser.add_argument(
        '-V', '--version',
        action='store_true',
        help="show version and exit",
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="give more output",
    )
    parser.add_argument(
        '--log',
        action='store',
        help="path to a verbose appending log",
    )


def _print_config(func):
    from ezdxf import options
    func(f"ezdxf v{__version__} @ {Path(__file__).parent}")
    func(f"Python version: {sys.version}")
    func(f"using C-extensions: {YES_NO[USE_C_EXT]}")
    func(f"using Matplotlib: {YES_NO[options.use_matplotlib]}")


def print_version():
    _print_config(print)


def setup_log(args):
    import logging
    from datetime import datetime
    level = "DEBUG" if args.verbose else "INFO"
    logging.basicConfig(filename=args.log, level=level)
    print(f"Appending logs to file \"{args.log}\", logging level: {level}\n")
    logger = logging.getLogger('ezdxf')
    logger.info("***** Launch time: " + datetime.now().isoformat() + " *****")
    if args.verbose:
        _print_config(logger.info)


DESCRIPTION = """
Command launcher for the Python package "ezdxf": https://pypi.org/project/ezdxf/

"""


def main():
    parser = argparse.ArgumentParser(
        "ezdxf",
        description=DESCRIPTION,
    )
    add_common_arguments(parser)
    subparsers = parser.add_subparsers(dest="command")
    commands.add_parsers(subparsers)

    args = parser.parse_args(sys.argv[1:])
    help_ = True
    options.log_unprocessed_tags = args.verbose
    if args.log:
        setup_log(args)
    if args.version:
        print_version()
        help_ = False

    run = commands.get(args.command)
    if run:
        # For the case automatic font loading is disabled:
        fonts.load()
        run(args)
    elif help_:
        parser.print_help()


if __name__ == "__main__":
    main()
