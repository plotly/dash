# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Upload(Component):
    """An Upload component.
    Upload components allow your app to accept user-uploaded files via drag'n'drop

    Keyword arguments:

    - children (a list of or a singular dash component, string or number | string; optional):
        Contents of the upload component.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - accept (string; optional):
        Allow specific types of files. See
        https://github.com/okonet/attr-accept for more information. Keep
        in mind that mime type determination is not reliable across
        platforms. CSV files, for example, are reported as text/plain
        under macOS but as application/vnd.ms-excel under Windows. In some
        cases there might not be a mime type set at all. See:
        https://github.com/react-dropzone/react-dropzone/issues/276.

    - className (string; optional):
        HTML class name of the component.

    - className_active (string; optional):
        HTML class name of the component while active.

    - className_disabled (string; optional):
        HTML class name of the component if disabled.

    - className_reject (string; optional):
        HTML class name of the component if rejected.

    - contents (string | list of strings; optional):
        The contents of the uploaded file as a binary string.

    - disable_click (boolean; default False):
        Disallow clicking on the component to open the file dialog.

    - disabled (boolean; default False):
        Enable/disable the upload component entirely.

    - filename (string | list of strings; optional):
        The name of the file(s) that was(were) uploaded. Note that this
        does not include the path of the file (for security reasons).

    - last_modified (number | list of numbers; optional):
        The last modified date of the file that was uploaded in unix time
        (seconds since 1970).

    - loading_state (dict; optional):
        Object that holds the loading state object coming from
        dash-renderer.

        `loading_state` is a dict with keys:

        - component_name (string; optional):
            Holds the name of the component that is loading.

        - is_loading (boolean; optional):
            Determines if the component is loading or not.

        - prop_name (string; optional):
            Holds which property is loading.

    - max_size (number; default -1):
        Maximum file size in bytes. If `-1`, then infinite.

    - min_size (number; default 0):
        Minimum file size in bytes.

    - multiple (boolean; default False):
        Allow dropping multiple files.

    - style (dict; optional):
        CSS styles to apply.

    - style_active (dict; default {    borderStyle: 'solid',    borderColor: '#6c6',    backgroundColor: '#eee',}):
        CSS styles to apply while active.

    - style_disabled (dict; default {    opacity: 0.5,}):
        CSS styles if disabled.

    - style_reject (dict; default {    borderStyle: 'solid',    borderColor: '#c66',    backgroundColor: '#eee',}):
        CSS styles if rejected."""

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Upload"

    @_explicitize_args
    def __init__(
        self,
        children=None,
        id=Component.UNDEFINED,
        contents=Component.UNDEFINED,
        filename=Component.UNDEFINED,
        last_modified=Component.UNDEFINED,
        accept=Component.UNDEFINED,
        disabled=Component.UNDEFINED,
        disable_click=Component.UNDEFINED,
        max_size=Component.UNDEFINED,
        min_size=Component.UNDEFINED,
        multiple=Component.UNDEFINED,
        className=Component.UNDEFINED,
        className_active=Component.UNDEFINED,
        className_reject=Component.UNDEFINED,
        className_disabled=Component.UNDEFINED,
        style=Component.UNDEFINED,
        style_active=Component.UNDEFINED,
        style_reject=Component.UNDEFINED,
        style_disabled=Component.UNDEFINED,
        loading_state=Component.UNDEFINED,
        **kwargs
    ):
        self._prop_names = [
            "children",
            "id",
            "accept",
            "className",
            "className_active",
            "className_disabled",
            "className_reject",
            "contents",
            "disable_click",
            "disabled",
            "filename",
            "last_modified",
            "loading_state",
            "max_size",
            "min_size",
            "multiple",
            "style",
            "style_active",
            "style_disabled",
            "style_reject",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "children",
            "id",
            "accept",
            "className",
            "className_active",
            "className_disabled",
            "className_reject",
            "contents",
            "disable_click",
            "disabled",
            "filename",
            "last_modified",
            "loading_state",
            "max_size",
            "min_size",
            "multiple",
            "style",
            "style_active",
            "style_disabled",
            "style_reject",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != "children"}

        super(Upload, self).__init__(children=children, **args)
