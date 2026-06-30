# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args
try:
    from dash.types import NumberType  # noqa: F401
except ImportError:
    # Backwards compatibility for dash<=4.1.0
    if typing.TYPE_CHECKING:
        raise
    NumberType = typing.Union[  # noqa: F401
        typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
    ]

ComponentSingleType = typing.Union[str, int, float, Component, None]
ComponentType = typing.Union[
    ComponentSingleType,
    typing.Sequence[ComponentSingleType],
]


class Upload_ReactComponent(Component):
    """An Upload_ReactComponent component.
The Upload component

Keyword arguments:

- id (string; default 'default-dash-uploader-id'):
    User supplied id of this component.

- cancelButton (boolean; default True):
    Whether or not to have a cancel button.

- chunkSize (number; default 1024 * 1024):
    Size of file chunks to send to server.

- className (string; default 'dash-uploader-default'):
    Class to add to the upload component by default.

- completeClass (string; default 'dash-uploader-complete'):
    Class to add to the upload component when it is complete.

- completeStyle (dict; optional):
    Style when upload is completed (upload finished).

- completedMessage (string; default 'Complete! '):
    Message to display when upload completed.

- defaultStyle (dict; optional):
    Style attributes to add to the upload component.

- disableDragAndDrop (boolean; default False):
    Whether or not to allow file drag and drop.

- disabled (boolean; default False):
    Whether or not to allow file uploading.

- disabledClass (string; default 'dash-uploader-disabled'):
    Class to add to the upload component when it is disabled.

- disabledMessage (string; default 'The uploader is disabled.'):
    Message to display when upload disabled.

- disabledStyle (dict; optional):
    Style when upload is disabled.

- fileNames (list of strings; optional):
    The names of the files uploaded.

- filetypes (list of strings; default undefined):
    List of allowed file types, e.g. ['jpg', 'png'].

- hoveredClass (string; default 'dash-uploader-hovered'):
    Class to add to the upload component when it is hovered.

- isCompleted (boolean; default False):
    The boolean flag telling if upload is completed.

- maxFileSize (number; default 1024 * 1024 * 10):
    Maximum size per file in bytes.

- maxFiles (number; default 1):
    Maximum number of files that can be uploaded in one session.

- pauseButton (boolean; default True):
    Whether or not to have a pause button.

- pausedClass (string; default 'dash-uploader-paused'):
    Class to add to the upload component when it is paused.

- service (string; default '/API/dash-uploader'):
    The service to send the files to.

- simultaneousUploads (number; optional):
    Number of simultaneous uploads to select.

- simultaneuosUploads (number; default 1):
    Number of simulaneous uploads.

- startButton (boolean; default True):
    Whether or not to have a start button.

- textLabel (string; default 'Click Here to Select a File'):
    The string to display in the upload component.

- upload_id (string; default ''):
    The ID for the upload event (for example, session ID).

- uploadingClass (string; default 'dash-uploader-uploading'):
    Class to add to the upload component when it is uploading.

- uploadingStyle (dict; optional):
    Style when upload is in progress."""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_uploader'
    _type = 'Upload_ReactComponent'


    def __init__(
        self,
        maxFiles: typing.Optional[NumberType] = None,
        maxFileSize: typing.Optional[NumberType] = None,
        chunkSize: typing.Optional[NumberType] = None,
        simultaneousUploads: typing.Optional[NumberType] = None,
        service: typing.Optional[str] = None,
        className: typing.Optional[str] = None,
        hoveredClass: typing.Optional[str] = None,
        disabledClass: typing.Optional[str] = None,
        pausedClass: typing.Optional[str] = None,
        completeClass: typing.Optional[str] = None,
        uploadingClass: typing.Optional[str] = None,
        defaultStyle: typing.Optional[dict] = None,
        disabledStyle: typing.Optional[dict] = None,
        uploadingStyle: typing.Optional[dict] = None,
        completeStyle: typing.Optional[dict] = None,
        textLabel: typing.Optional[str] = None,
        disabledMessage: typing.Optional[str] = None,
        completedMessage: typing.Optional[str] = None,
        fileNames: typing.Optional[typing.Sequence[str]] = None,
        filetypes: typing.Optional[typing.Sequence[str]] = None,
        startButton: typing.Optional[bool] = None,
        pauseButton: typing.Optional[bool] = None,
        cancelButton: typing.Optional[bool] = None,
        disabled: typing.Optional[bool] = None,
        disableDragAndDrop: typing.Optional[bool] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        isCompleted: typing.Optional[bool] = None,
        upload_id: typing.Optional[str] = None,
        simultaneuosUploads: typing.Optional[NumberType] = None,
        onUploadErrorCallback: typing.Optional[typing.Any] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'cancelButton', 'chunkSize', 'className', 'completeClass', 'completeStyle', 'completedMessage', 'defaultStyle', 'disableDragAndDrop', 'disabled', 'disabledClass', 'disabledMessage', 'disabledStyle', 'fileNames', 'filetypes', 'hoveredClass', 'isCompleted', 'maxFileSize', 'maxFiles', 'pauseButton', 'pausedClass', 'service', 'simultaneousUploads', 'simultaneuosUploads', 'startButton', 'textLabel', 'upload_id', 'uploadingClass', 'uploadingStyle']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'cancelButton', 'chunkSize', 'className', 'completeClass', 'completeStyle', 'completedMessage', 'defaultStyle', 'disableDragAndDrop', 'disabled', 'disabledClass', 'disabledMessage', 'disabledStyle', 'fileNames', 'filetypes', 'hoveredClass', 'isCompleted', 'maxFileSize', 'maxFiles', 'pauseButton', 'pausedClass', 'service', 'simultaneousUploads', 'simultaneuosUploads', 'startButton', 'textLabel', 'upload_id', 'uploadingClass', 'uploadingStyle']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Upload_ReactComponent, self).__init__(**args)

setattr(Upload_ReactComponent, "__init__", _explicitize_args(Upload_ReactComponent.__init__))
