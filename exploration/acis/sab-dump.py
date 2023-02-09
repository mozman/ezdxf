#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from argparse import ArgumentParser
from ezdxf.acis import api as acis


def main():
    parser = ArgumentParser()
    parser.add_argument("file", nargs=1)
    args = parser.parse_args()
    if args.file:
        with open(args.file[0], "rb") as fp:
            data = fp.read()
    print("\n".join(acis.dump_sab_as_text(data)))


if __name__ == "__main__":
    main()
