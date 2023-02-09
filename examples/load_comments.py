# Copyright (c) 2021-2022, Manfred Moitzi
# License: MIT License
import sys
from ezdxf import comments

# ------------------------------------------------------------------------------
# Ezdxf drops all comments from loaded DXF files.
# This example shows how to load comments from DXF files if needed.
#
# docs: https://ezdxf.mozman.at/docs/comments.html
# ------------------------------------------------------------------------------


def main():
    filename = sys.argv[1]
    comment_collector = []
    for code, value in comments.from_file(filename, codes={0, 5}):
        # get also handles and structure tags to associated prepending comments
        # to DXF entities
        if code == 5:
            handle = value
            print(f"Handle: {handle}")
            print("Prepending comments:")
            for comment in comment_collector:
                print(comment)
            comment_collector = []
        elif code == 0 and value == "ENDSEC":
            # delete collected comments at end of section like the HEADER section
            # this removes 'noise'.
            comment_collector = []
        elif code == 999:
            comment_collector.append(value)


if __name__ == "__main__":
    main()
