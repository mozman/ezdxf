# Copyright (c) 2020, Joseph Flack
# License: MIT License
from typing import TYPE_CHECKING, Optional
import io
import base64
import ezdxf
from ezdxf.filemanagement import dxf_stream_info

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing


def get_dxf_doc_from_upload_data(data: bytes) -> Optional['Drawing']:
    """
    This function turns the dxf data provided by Dash Plotly upload component into an `ezdxf` doc
    Dash plotly upload component only provides base 64 encoded data.

    Args:
        data: DXF document uploaded as base64 encoded data

    Returns:
        DXF document as Drawing() object

    """
    if data is None:
        return None

    # turn contents list into string. Contents is 64 encoded as per dash plotly
    contents = str(data)
    # remove the first part of the decoded info Raw Content
    # example: data:application/vnd.ms-excel;base64,ICAwU0VDVElPTiAgMkhFQURFUiAgOSRBQ0FEVkVSICAxQUMxMDI0ICA5JEFDQURNQUlOVFZFUiA3MDYgIDkkRFdHQ09ERVBBR0
    content_type, content_string = contents.split(',')
    # Decode this into binary data string
    binary_decoded_unformatted = base64.b64decode(content_string)
    # fix the end of line problem for the EOF. ie remove the last \r\n so
    # EZDXF can find the EOF:
    binary_decoded_no_EOF = binary_decoded_unformatted.rstrip(b'\r\n')
    # Change the \r\n encoding (from windows / 64 encoding) to \n (ezdxf compatible)
    binary_decoded = binary_decoded_no_EOF.replace(b'\r\n', b'\n')
    # decode this into unicode utf-8 which is the format required for dxf
    utf_decoded = binary_decoded.decode("utf-8", errors="ignore")
    # Create stringIO object to treat the data like a file and write the data to the object
    # like a file opened in text mode https://docs.python.org/3/library/io.html
    temp_tx_stream = io.StringIO(utf_decoded)
    # Get info about the file
    info = dxf_stream_info(temp_tx_stream)
    encoding = info.encoding
    # Re code the binary data using the encoding found in the "info":
    decoded_data = binary_decoded.decode(encoding, errors="ignore")
    # Create new text stream for use on the correctly decoded data:
    tx_stream = io.StringIO(decoded_data)
    # read the text stream
    doc = ezdxf.read(tx_stream)
    # Close the other stream IO objects used for reading the file contents
    tx_stream.close()
    temp_tx_stream.close()
    return doc
