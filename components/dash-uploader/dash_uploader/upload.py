import uuid

from dash_uploader._build.Upload_ReactComponent import Upload_ReactComponent
import dash_uploader.settings as settings

DEFAULT_STYLE = {
    "width": "100%",
    # min-height and line-height should be the same to make
    # the centering work.
    "minHeight": "100px",
    "lineHeight": "100px",
    "textAlign": "center",
    "borderWidth": "1px",
    "borderStyle": "dashed",
    "borderRadius": "7px",
}


def update_upload_api(requests_pathname_prefix, upload_api):
    """Path join for the API path name.
    This is a private method, and should not be exposed to users.
    """
    if requests_pathname_prefix == "/":
        return upload_api
    return "/".join(
        [
            requests_pathname_prefix.rstrip("/"),
            upload_api.lstrip("/"),
        ]
    )


def combine(overiding_dict, base_dict):
    """Combining two dictionaries without modifying them.
    This is a private method, and should not be exposed to users.
    """
    if overiding_dict is None:
        return dict(base_dict)
    return {**base_dict, **overiding_dict}


# Implemented as function, but still uppercase.
# This is because subclassing the Dash-auto-generated
# "Upload from Upload.py" will give some errors
def Upload(
    id="dash-uploader",
    text="Drag and Drop Here to upload!",
    text_completed="Uploaded: ",
    text_disabled="The uploader is disabled.",
    cancel_button=True,
    pause_button=False,
    disabled=False,
    filetypes=None,
    max_file_size=1024,
    chunk_size=1,
    default_style=None,
    upload_id=None,
    max_files=1,
):
    """
    du.Upload component

    Parameters
    ----------
    text: str
        The text to show in the upload "Drag
        and Drop" area. Optional.
    text_completed: str
        The text to show in the upload area
        after upload has completed successfully before
        the name of the uploaded file. For example, if user
        uploaded "data.zip" and `text_completed` is
        "Ready! ", then user would see text "Ready!
        data.zip".
    text_disabled: str
        The text to show in the upload area when the
        the component is disabled.
    cancel_button: bool
        If True, shows a cancel button.
    pause_button: bool
        If True, shows a pause button.
    disabled: bool
        If True, the file is not allowed to be uploaded.
    filetypes: list of str or None
        The filetypes that can be uploaded.
        For example ['zip', 'rar'].
        Note that this just checks the extension of the
        filename, and user might still upload any kind
        of file (by renaming)!
        By default, all filetypes are accepted.
    max_file_size: numeric
        The maximum file size in Megabytes. Optional.
    chunk_size: numeric
        The chunk size in Megabytes. Optional.
    default_style: None or dict
        Inline CSS styling for the main div element.
        If None, use the default style of the component.
        If dict, will use the union on the given dict
        and the default style. (you may override
        part of the style by giving a dictionary)
        More styling options through the CSS classes.
    upload_id: None or str
        The upload id, created with uuid.uuid1() or uuid.uuid4(),
        for example. If none, creates random session id with
        uuid.uuid1().
    max_files: int (default: 1)
        EXPERIMENTAL feature. Read below. For bulletproof
        implementation, force usage of zip files and keep
        max_files = 1.

        The number of files that can be added to
        the upload field simultaneously.

        Notes:
        (1) If even a single file which is not supported file
         type, is added to the upload queue, upload process of
         all files will be permanently interrupted.
        (2) Use reasonably small amount in "max_files".
        (3) When uploading two folders with Chrome, there is
         a bug in resumable.js which makes only one of the
         folders to be uploaded. See:
         https://github.com/23/resumable.js/issues/416
        (4) When uploading folders, note that the subdirectories
          are NOT created -> All files in the folders will
          be uploaded to the single upload folder.

    Returns
    -------
    Upload: dash component
        Initiated Dash component for app.layout.
    """

    # Handle styling
    default_style = combine(default_style, DEFAULT_STYLE)
    disabled_style = combine({"opacity": "0.5"}, default_style)
    upload_style = combine({"lineHeight": "0px"}, default_style)

    if upload_id is None:
        upload_id = uuid.uuid1()

    service = update_upload_api(settings.requests_pathname_prefix, settings.upload_api)

    arguments = dict(
        id=id,
        isCompleted=False,
        # Have not tested if using many files
        # is reliable -> Do not allow
        maxFiles=max_files,
        maxFileSize=max_file_size * 1024 * 1024,
        chunkSize=chunk_size * 1024 * 1024,
        textLabel=text,
        service=service,
        startButton=False,
        disabled=disabled,
        # Not tested so default to one.
        simultaneousUploads=1,
        completedMessage=text_completed,
        disabledMessage=text_disabled,
        cancelButton=cancel_button,
        pauseButton=pause_button,
        defaultStyle=default_style,
        disabledStyle=disabled_style,
        uploadingStyle=upload_style,
        completeStyle=default_style,
        upload_id=str(upload_id),
    )

    if filetypes:
        arguments["filetypes"] = filetypes

    return Upload_ReactComponent(**arguments)
