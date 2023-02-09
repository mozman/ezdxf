# Copyright (c) 2020, Joseph Flack
# License: MIT License
import ezdxf
from ezdxf.document import Drawing

# ------------------------------------------------------------------------------
# encode and decode DXF documents as base64 data for upload and download in web
# applications
# ------------------------------------------------------------------------------


def get_dxf_doc_from_upload_data(data: bytes) -> Drawing:
    """
    This function turns the DXF data provided by Dash Plotly upload component
    into an `ezdxf` DXF document. Dash plotly upload component only provides
    base 64 encoded data.

    Args:
        data: DXF document uploaded as base64 encoded data

    Returns:
        DXF document as Drawing() object

    """
    # Remove the mime-type and encoding info from data
    # example: data:application/octet-stream;base64,OTk5DQpkeGZydyAwLjYuMw0KICAwDQpTRUNUSU9ODQogIDINCkhFQURFUg0KICA...
    _, data = data.split(b",")
    return ezdxf.decode_base64(data)


def encode_base64(doc: Drawing) -> bytes:
    return b"data:application/octet-stream;base64," + doc.encode_base64()


if __name__ == "__main__":
    data = encode_base64(ezdxf.new())
    doc = get_dxf_doc_from_upload_data(data)
    print(doc.acad_release)
