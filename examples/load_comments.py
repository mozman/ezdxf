import sys
from ezdxf.lldxf.validator import is_dxf_file
from ezdxf.filemanagement import dxf_file_info


def load_comments(stream):
    line = 1
    while True:
        try:
            code = stream.readline()
            value = stream.readline()
        except EOFError:
            return
        if code and value:  # StringIO(): empty strings indicates EOF
            try:
                code = int(code)
            except ValueError:
                raise ValueError('Invalid group code "{}" at line {}.'.format(code, line))
            else:
                if code == 999:  # just yield comments
                    yield value.rstrip('\n')
                line += 2
        else:
            return


def open_stream(filename):
    if is_dxf_file(filename):
        info = dxf_file_info(filename)
        return open(filename, mode='rt', encoding=info.encoding)
    else:
        raise IOError('File "{}" is not a DXF file.'.format(filename))


if __name__ == '__main__':
    filename = sys.argv[1]
    stream = open_stream(filename)
    try:
        for comment in load_comments(stream):
            print(comment)
    finally:
        stream.close()
