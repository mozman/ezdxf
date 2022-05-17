#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from argparse import ArgumentParser
from ezdxf.acis import sab


def print_entity(e):
    for tag, value in e:
        name = sab.Tags(tag).name
        print(f"{name} = {value}")


def dump_sab(data: bytes):
    decoder = sab.Decoder(data)
    header = decoder.read_header()
    print("\n".join(header.dumps()))
    index = 0
    try:
        for record in decoder.read_records():
            print(f"--------------------- record: {index}")
            print_entity(record)
            index += 1
    except sab.ParsingError as e:
        print(str(e))


def main():
    parser = ArgumentParser()
    parser.add_argument("file", nargs=1)
    args = parser.parse_args()
    if args.file:
        with open(args.file[0], "rb") as fp:
            data = fp.read()
    dump_sab(data)


if __name__ == "__main__":
    main()
