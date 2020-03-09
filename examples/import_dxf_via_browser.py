# Copyright (c) 2020, Joseph Flack
# License: MIT License
from typing import TYPE_CHECKING
import io
import base64
import ezdxf
from ezdxf.filemanagement import dxf_stream_info

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing


def get_dxf_doc_from_upload_data(data: bytes) -> 'Drawing':
    """
    This function turns the DXF data provided by Dash Plotly upload component into an `ezdxf` DXF document.
    Dash plotly upload component only provides base 64 encoded data.

    Args:
        data: DXF document uploaded as base64 encoded data

    Returns:
        DXF document as Drawing() object

    """
    # Remove the mime-type and encoding info from data
    # example: data:application/vnd.ms-excel;base64,ICAwU0VDVElPTiAgMkhFQURFUiAgOSRBQ0FEVkVSICAxQUMxMDI0ICA5JEFDQ...
    _, data = data.split(b',')

    # Decode base64 encoded data into binary data
    binary_data = base64.b64decode(data)

    # Replace windows line ending '\r\n' by universal line ending '\n'
    binary_data = binary_data.replace(b'\r\n', b'\n')

    # Read DXF file info from data, basic DXF information in the HEADER section is ASCII encoded
    # so encoding setting here is not important for this task:
    text = binary_data.decode('utf-8', errors='ignore')
    stream = io.StringIO(text)
    info = dxf_stream_info(stream)
    stream.close()

    # Use encoding info to create correct decoded text input stream for ezdxf
    text = binary_data.decode(info.encoding, errors='ignore')
    stream = io.StringIO(text)

    # Load DXF document from data stream
    doc = ezdxf.read(stream)
    stream.close()
    return doc


def example_data(doc: 'Drawing') -> bytes:
    stream = io.StringIO()
    doc.write(stream)
    # create binary data with windows line ending
    binary_data = stream.getvalue().encode('utf-8').replace(b'\n', b'\r\n')
    return b'data:application/any;base64,' + base64.encodebytes(binary_data)


if __name__ == '__main__':
    data = example_data(ezdxf.new())
    doc = get_dxf_doc_from_upload_data(data)
    print(doc.acad_release)
