def create_file(filename, filesize_mb=1):
    """
    Create file for testing purposes.

    Parameters
    ----------
    filename: str
        The filename
    filesize_mb: numeric
        The file size in Mb.
    """
    with open(filename, "wb") as f:
        f.seek(1024 * 1024 * filesize_mb)
        f.write(b"0")


def load_text_file(file_path):
    """
    Load text file from the path

    Parameters
    ----------
    file_path: str
        The path of the file.
    """
    with open(file_path, "r") as f:
        return f.read()
