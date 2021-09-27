# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
import sys
from ezdxf import comments

if __name__ == "__main__":
    filename = sys.argv[1]
    comment_collector = []
    for code, value in comments.from_file(filename, codes={0, 5}):
        # get also handles and structure tags to associated prepending comments to DXF entities
        if code == 5:
            handle = value
            print("Handle: {}".format(value))
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
