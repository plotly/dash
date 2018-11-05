# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Input(Component):
    """A Input component.
A basic HTML input control for entering text, numbers, or passwords.

Note that checkbox and radio types are supported through
the Checklist and RadioItems component. Dates, times, and file uploads
are also supported through separate components.

Keyword arguments:
- id (string; optional): The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.
- value (string | number; optional): The value of the input
- style (dict; optional): The input's inline styles
- className (string; optional): The class of the input element
- debounce (boolean; optional): If true, changes to input will be sent back to the Dash server only on enter or when losing focus.
If it's false, it will sent the value back on every change.
- type (a value equal to: "text", 'number', 'password', 'email', 'range', 'search', 'tel', 'url', 'hidden'; optional): The type of control to render.
- autocomplete (string; optional): This attribute indicates whether the value of the control can be automatically completed by the browser.
- autofocus (string; optional): The element should be automatically focused after the page loaded.
- disabled (boolean; optional): If true, the input is disabled and can't be clicked on.
- inputmode (a value equal to: "verbatim", "latin", "latin-name", "latin-prose", "full-width-latin", "kana", "katakana", "numeric", "tel", "email", "url"; optional)
- list (string; optional): Identifies a list of pre-defined options to suggest to the user.
The value must be the id of a <datalist> element in the same document.
The browser displays only options that are valid values for this
input element.
This attribute is ignored when the type attribute's value is
hidden, checkbox, radio, file, or a button type.
- max (string | number; optional): The maximum (numeric or date-time) value for this item, which must not be less than its minimum (min attribute) value.
- maxlength (string; optional): If the value of the type attribute is text, email, search, password, tel, or url, this attribute specifies the maximum number of characters (in UTF-16 code units) that the user can enter. For other control types, it is ignored. It can exceed the value of the size attribute. If it is not specified, the user can enter an unlimited number of characters. Specifying a negative number results in the default behavior (i.e. the user can enter an unlimited number of characters). The constraint is evaluated only when the value of the attribute has been changed.
- min (string | number; optional): The minimum (numeric or date-time) value for this item, which must not be greater than its maximum (max attribute) value.
- minlength (string; optional): If the value of the type attribute is text, email, search, password, tel, or url, this attribute specifies the minimum number of characters (in Unicode code points) that the user can enter. For other control types, it is ignored.
- multiple (boolean; optional): This Boolean attribute indicates whether the user can enter more than one value. This attribute applies when the type attribute is set to email or file, otherwise it is ignored.
- name (string; optional): The name of the control, which is submitted with the form data.
- pattern (string; optional): A regular expression that the control's value is checked against. The pattern must match the entire value, not just some subset. Use the title attribute to describe the pattern to help the user. This attribute applies when the value of the type attribute is text, search, tel, url, email, or password, otherwise it is ignored. The regular expression language is the same as JavaScript RegExp algorithm, with the 'u' parameter that makes it treat the pattern as a sequence of unicode code points. The pattern is not surrounded by forward slashes.
- placeholder (string; optional): A hint to the user of what can be entered in the control . The placeholder text must not contain carriage returns or line-feeds. Note: Do not use the placeholder attribute instead of a <label> element, their purposes are different. The <label> attribute describes the role of the form element (i.e. it indicates what kind of information is expected), and the placeholder attribute is a hint about the format that the content should take. There are cases in which the placeholder attribute is never displayed to the user, so the form must be understandable without it.
- readOnly (string; optional): This attribute indicates that the user cannot modify the value of the control. The value of the attribute is irrelevant. If you need read-write access to the input value, do not add the "readonly" attribute. It is ignored if the value of the type attribute is hidden, range, color, checkbox, radio, file, or a button type (such as button or submit).
- required (string; optional): This attribute specifies that the user must fill in a value before submitting a form. It cannot be used when the type attribute is hidden, image, or a button type (submit, reset, or button). The :optional and :required CSS pseudo-classes will be applied to the field as appropriate.
- selectionDirection (string; optional): The direction in which selection occurred. This is "forward" if the selection was made from left-to-right in an LTR locale or right-to-left in an RTL locale, or "backward" if the selection was made in the opposite direction. On platforms on which it's possible this value isn't known, the value can be "none"; for example, on macOS, the default direction is "none", then as the user begins to modify the selection using the keyboard, this will change to reflect the direction in which the selection is expanding.
- selectionEnd (string; optional): The offset into the element's text content of the last selected character. If there's no selection, this value indicates the offset to the character following the current text input cursor position (that is, the position the next character typed would occupy).
- selectionStart (string; optional): The offset into the element's text content of the first selected character. If there's no selection, this value indicates the offset to the character following the current text input cursor position (that is, the position the next character typed would occupy).
- size (string; optional): The initial size of the control. This value is in pixels unless the value of the type attribute is text or password, in which case it is an integer number of characters. Starting in, this attribute applies only when the type attribute is set to text, search, tel, url, email, or password, otherwise it is ignored. In addition, the size must be greater than zero. If you do not specify a size, a default value of 20 is used.' simply states "the user agent should ensure that at least that many characters are visible", but different characters can have different widths in certain fonts. In some browsers, a certain string with x characters will not be entirely visible even if size is defined to at least x.
- spellCheck (string; optional): Setting the value of this attribute to true indicates that the element needs to have its spelling and grammar checked. The value default indicates that the element is to act according to a default behavior, possibly based on the parent element's own spellcheck value. The value false indicates that the element should not be checked.
- step (string | number; optional): Works with the min and max attributes to limit the increments at which a numeric or date-time value can be set. It can be the string any or a positive floating point number. If this attribute is not set to any, the control accepts only values at multiples of the step value greater than the minimum.
- n_submit (number; optional): Number of times the `Enter` key was pressed while the input had focus.
- n_submit_timestamp (number; optional): Last time that `Enter` was pressed.
- n_blur (number; optional): Number of times the input lost focus.
- n_blur_timestamp (number; optional): Last time the input lost focus.

Available events: 'blur', 'change'"""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, value=Component.UNDEFINED, style=Component.UNDEFINED, className=Component.UNDEFINED, debounce=Component.UNDEFINED, type=Component.UNDEFINED, autocomplete=Component.UNDEFINED, autofocus=Component.UNDEFINED, disabled=Component.UNDEFINED, inputmode=Component.UNDEFINED, list=Component.UNDEFINED, max=Component.UNDEFINED, maxlength=Component.UNDEFINED, min=Component.UNDEFINED, minlength=Component.UNDEFINED, multiple=Component.UNDEFINED, name=Component.UNDEFINED, pattern=Component.UNDEFINED, placeholder=Component.UNDEFINED, readOnly=Component.UNDEFINED, required=Component.UNDEFINED, selectionDirection=Component.UNDEFINED, selectionEnd=Component.UNDEFINED, selectionStart=Component.UNDEFINED, size=Component.UNDEFINED, spellCheck=Component.UNDEFINED, step=Component.UNDEFINED, n_submit=Component.UNDEFINED, n_submit_timestamp=Component.UNDEFINED, n_blur=Component.UNDEFINED, n_blur_timestamp=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'value', 'style', 'className', 'debounce', 'type', 'autocomplete', 'autofocus', 'disabled', 'inputmode', 'list', 'max', 'maxlength', 'min', 'minlength', 'multiple', 'name', 'pattern', 'placeholder', 'readOnly', 'required', 'selectionDirection', 'selectionEnd', 'selectionStart', 'size', 'spellCheck', 'step', 'n_submit', 'n_submit_timestamp', 'n_blur', 'n_blur_timestamp']
        self._type = 'Input'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_events = ['blur', 'change']
        self.available_properties = ['id', 'value', 'style', 'className', 'debounce', 'type', 'autocomplete', 'autofocus', 'disabled', 'inputmode', 'list', 'max', 'maxlength', 'min', 'minlength', 'multiple', 'name', 'pattern', 'placeholder', 'readOnly', 'required', 'selectionDirection', 'selectionEnd', 'selectionStart', 'size', 'spellCheck', 'step', 'n_submit', 'n_submit_timestamp', 'n_blur', 'n_blur_timestamp']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Input, self).__init__(**args)

    def __repr__(self):
        if(any(getattr(self, c, None) is not None
               for c in self._prop_names
               if c is not self._prop_names[0])
           or any(getattr(self, c, None) is not None
                  for c in self.__dict__.keys()
                  if any(c.startswith(wc_attr)
                  for wc_attr in self._valid_wildcard_attributes))):
            props_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self._prop_names
                                      if getattr(self, c, None) is not None])
            wilds_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self.__dict__.keys()
                                      if any([c.startswith(wc_attr)
                                      for wc_attr in
                                      self._valid_wildcard_attributes])])
            return ('Input(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                'Input(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')
