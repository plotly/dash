# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class SyntaxHighlighter(Component):
    """A SyntaxHighlighter component.
A component for pretty printing code.

Keyword arguments:
- children (string | list; optional): The text to display and highlight
- id (string; optional)
- language (string; optional): the language to highlight code in.
- theme (a value equal to: 'light', 'dark'; optional): theme: light or dark
- customStyle (dict; optional): prop that will be combined with the top level style on the pre tag, styles here will overwrite earlier styles.
- codeTagProps (dict; optional): props that will be spread into the <code> tag that is the direct parent of the highlighted code elements. Useful for styling/assigning classNames.
- useInlineStyles (boolean; optional): if this prop is passed in as false, react syntax highlighter will not add style objects to elements, and will instead append classNames. You can then style the code block by using one of the CSS files provided by highlight.js.
- showLineNumbers (boolean; optional): if this is enabled line numbers will be shown next to the code block.
- startingLineNumber (number; optional): if showLineNumbers is enabled the line numbering will start from here.
- lineNumberContainerStyle (dict; optional): the line numbers container default to appearing to the left with 10px of right padding. You can use this to override those styles.
- lineNumberStyle (dict; optional): inline style to be passed to the span wrapping each number. Can be either an object or a function that recieves current line number as argument and returns style object.
- wrapLines (boolean; optional): a boolean value that determines whether or not each line of code should be wrapped in a parent element. defaults to false, when false one can not take action on an element on the line level. You can see an example of what this enables here
- lineStyle (dict; optional): inline style to be passed to the span wrapping each line if wrapLines is true. Can be either an object or a function that recieves current line number as argument and returns style object.
- loading_state (optional): Object that holds the loading state object coming from dash-renderer. loading_state has the following type: dict containing keys 'is_loading', 'prop_name', 'component_name'.
Those keys have the following types:
  - is_loading (boolean; optional): Determines if the component is loading or not
  - prop_name (string; optional): Holds which property is loading
  - component_name (string; optional): Holds the name of the component that is loading"""
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, language=Component.UNDEFINED, theme=Component.UNDEFINED, customStyle=Component.UNDEFINED, codeTagProps=Component.UNDEFINED, useInlineStyles=Component.UNDEFINED, showLineNumbers=Component.UNDEFINED, startingLineNumber=Component.UNDEFINED, lineNumberContainerStyle=Component.UNDEFINED, lineNumberStyle=Component.UNDEFINED, wrapLines=Component.UNDEFINED, lineStyle=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'language', 'theme', 'customStyle', 'codeTagProps', 'useInlineStyles', 'showLineNumbers', 'startingLineNumber', 'lineNumberContainerStyle', 'lineNumberStyle', 'wrapLines', 'lineStyle', 'loading_state']
        self._type = 'SyntaxHighlighter'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'language', 'theme', 'customStyle', 'codeTagProps', 'useInlineStyles', 'showLineNumbers', 'startingLineNumber', 'lineNumberContainerStyle', 'lineNumberStyle', 'wrapLines', 'lineStyle', 'loading_state']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(SyntaxHighlighter, self).__init__(children=children, **args)
