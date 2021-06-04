import io
import ntpath
import base64
from functools import partial

# Py2 StringIO.StringIO handles unicode but io.StringIO doesn't
try:
    from StringIO import StringIO as _StringIO
    py2 = True
except ImportError:
    _StringIO = io.StringIO
    py2 = False

# region Utils for Download component


def send_file(path, filename=None, type=None):
    """
    Convert a file into the format expected by the Download component.
    :param path: path to the file to be sent
    :param filename: name of the file, if not provided the original filename is used
    :param type: type of the file (optional, passed to Blob in the javascript layer)
    :return: dict of file content (base64 encoded) and meta data used by the Download component
    """
    # If filename is not set, read it from the path.
    if filename is None:
        filename = ntpath.basename(path)
    # Read the file contents and send it.
    with open(path, "rb") as f:
        return send_bytes(f.read(), filename, type)


def send_bytes(src, filename, type=None, **kwargs):
    """
    Convert data written to BytesIO into the format expected by the Download component.
    :param src: array of bytes or a writer that can write to BytesIO
    :param filename: the name of the file
    :param type: type of the file (optional, passed to Blob in the javascript layer)
    :return: dict of data frame content (base64 encoded) and meta data used by the Download component
    """
    content = src if isinstance(src, bytes) else _io_to_str(io.BytesIO(), src, **kwargs)
    return dict(
        content=base64.b64encode(content).decode(),
        filename=filename,
        type=type,
        base64=True,
    )


def send_string(src, filename, type=None, **kwargs):
    """
    Convert data written to StringIO into the format expected by the Download component.
    :param src: a string or a writer that can write to StringIO
    :param filename: the name of the file
    :param type: type of the file (optional, passed to Blob in the javascript layer)
    :return: dict of data frame content (NOT base64 encoded) and meta data used by the Download component
    """
    content = src if isinstance(src, str) else _io_to_str(_StringIO(), src, **kwargs)
    return dict(content=content, filename=filename, type=type, base64=False)


def _io_to_str(data_io, writer, **kwargs):
    # Some pandas writers try to close the IO, we do not want that.
    data_io_close = data_io.close
    data_io.close = lambda: None
    # Write data content.
    writer(data_io, **kwargs)
    data_value = data_io.getvalue()
    data_io_close()
    return data_value


def send_data_frame(writer, filename, type=None, **kwargs):
    """
    Convert data frame into the format expected by the Download component.
    :param writer: a data frame writer
    :param filename: the name of the file
    :param type: type of the file (optional, passed to Blob in the javascript layer)
    :return: dict of data frame content (base64 encoded) and meta data used by the Download component

    Examples
    --------

    >>> df = pd.DataFrame({'a': [1, 2, 3, 4], 'b': [2, 1, 5, 6], 'c': ['x', 'x', 'y', 'y']})
    ...
    >>> send_data_frame(df.to_csv, "mydf.csv")  # download as csv
    >>> send_data_frame(df.to_json, "mydf.json")  # download as json
    >>> send_data_frame(df.to_excel, "mydf.xls", index=False) # download as excel
    >>> send_data_frame(df.to_pickle, "mydf.pkl") # download as pickle

    """
    name = writer.__name__
    # Check if the provided writer is known.
    if name not in _data_frame_senders.keys():
        raise ValueError(
            "The provided writer ({}) is not supported, "
            "try calling send_string or send_bytes directly.".format(name)
        )
    # Send data frame using the appropriate send function.
    return _data_frame_senders[name](writer, filename, type, **kwargs)


_data_frame_senders = {
    "to_csv": send_string,
    "to_json": send_string,
    "to_html": send_string,
    "to_excel": send_bytes,
    "to_feather": send_bytes,
    "to_parquet": send_bytes,
    "to_msgpack": send_bytes,
    "to_stata": send_bytes,
    "to_pickle": partial(send_bytes, compression=None) if py2 else send_bytes,
}

# endregion
