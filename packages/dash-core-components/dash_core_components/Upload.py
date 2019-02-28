# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Upload(Component):
    """A Upload component.


Keyword arguments:
- children (a list of or a singular dash component, string or number | string; optional): Contents of the upload component
- id (string; optional): ID of the component. Used to identify component
in Dash callback functions.
- contents (string | list; optional): The contents of the uploaded file as a binary string
- filename (string | list; optional): The name of the file(s) that was(were) uploaded.
Note that this does not include the path of the file
(for security reasons).
- last_modified (number | list; optional): The last modified date of the file that was uploaded in unix time
(seconds since 1970).
- accept (string; optional): Allow specific types of files.
See https://github.com/okonet/attr-accept for more information.
Keep in mind that mime type determination is not reliable across
platforms. CSV files, for example, are reported as text/plain
under macOS but as application/vnd.ms-excel under Windows.
In some cases there might not be a mime type set at all.
See: https://github.com/react-dropzone/react-dropzone/issues/276
- disabled (boolean; optional): Enable/disable the upload component entirely
- disable_click (boolean; optional): Disallow clicking on the component to open the file dialog
- max_size (number; optional): Maximum file size. If `-1`, then infinite
- min_size (number; optional): Minimum file size
- multiple (boolean; optional): Allow dropping multiple files
- className (string; optional): HTML class name of the component
- className_active (string; optional): HTML class name of the component while active
- className_reject (string; optional): HTML class name of the component if rejected
- className_disabled (string; optional): HTML class name of the component if disabled
- style (dict; optional): CSS styles to apply
- style_active (dict; optional): CSS styles to apply while active
- style_reject (dict; optional): CSS styles if rejected
- style_disabled (dict; optional): CSS styles if disabled
- loading_state (optional): Object that holds the loading state object coming from dash-renderer. loading_state has the following type: dict containing keys 'is_loading', 'prop_name', 'component_name'.
Those keys have the following types:
  - is_loading (boolean; optional): Determines if the component is loading or not
  - prop_name (string; optional): Holds which property is loading
  - component_name (string; optional): Holds the name of the component that is loading"""
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, contents=Component.UNDEFINED, filename=Component.UNDEFINED, last_modified=Component.UNDEFINED, accept=Component.UNDEFINED, disabled=Component.UNDEFINED, disable_click=Component.UNDEFINED, max_size=Component.UNDEFINED, min_size=Component.UNDEFINED, multiple=Component.UNDEFINED, className=Component.UNDEFINED, className_active=Component.UNDEFINED, className_reject=Component.UNDEFINED, className_disabled=Component.UNDEFINED, style=Component.UNDEFINED, style_active=Component.UNDEFINED, style_reject=Component.UNDEFINED, style_disabled=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'contents', 'filename', 'last_modified', 'accept', 'disabled', 'disable_click', 'max_size', 'min_size', 'multiple', 'className', 'className_active', 'className_reject', 'className_disabled', 'style', 'style_active', 'style_reject', 'style_disabled', 'loading_state']
        self._type = 'Upload'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'contents', 'filename', 'last_modified', 'accept', 'disabled', 'disable_click', 'max_size', 'min_size', 'multiple', 'className', 'className_active', 'className_reject', 'className_disabled', 'style', 'style_active', 'style_reject', 'style_disabled', 'loading_state']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Upload, self).__init__(children=children, **args)
