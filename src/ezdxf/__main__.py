#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import sys
import argparse
from ezdxf import options, print_config
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


def print_version(verbose=False):
    print_config(print, verbose=verbose)


def setup_log(args):
    import logging
    from datetime import datetime
    level = "DEBUG" if args.verbose else "INFO"
    logging.basicConfig(filename=args.log, level=level)
    print(f"Appending logs to file \"{args.log}\", logging level: {level}\n")
    logger = logging.getLogger('ezdxf')
    logger.info("***** Launch time: " + datetime.now().isoformat() + " *****")
    if args.verbose:
        print_config(logger.info, verbose=True)


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
        print_version(args.verbose)
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
