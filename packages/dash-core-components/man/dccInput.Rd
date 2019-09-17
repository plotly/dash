% Auto-generated: do not edit by hand
\name{dccInput}

\alias{dccInput}

\title{Input component}

\description{
A basic HTML input control for entering text, numbers, or passwords.  Note that checkbox and radio types are supported through the Checklist and RadioItems component. Dates, times, and file uploads are also supported through separate components.
}

\usage{
dccInput(id=NULL, value=NULL, style=NULL, className=NULL, debounce=NULL, type=NULL,
autoComplete=NULL, autoFocus=NULL, disabled=NULL, inputMode=NULL, list=NULL,
max=NULL, maxLength=NULL, min=NULL, minLength=NULL, multiple=NULL, name=NULL,
pattern=NULL, placeholder=NULL, readOnly=NULL, required=NULL,
selectionDirection=NULL, selectionEnd=NULL, selectionStart=NULL, size=NULL,
spellCheck=NULL, step=NULL, n_submit=NULL, n_submit_timestamp=NULL, n_blur=NULL,
n_blur_timestamp=NULL, loading_state=NULL, persistence=NULL,
persisted_props=NULL, persistence_type=NULL)
}

\arguments{
\item{id}{Character. The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{value}{Character | numeric. The value of the input}

\item{style}{Named list. The input's inline styles}

\item{className}{Character. The class of the input element}

\item{debounce}{Logical. If true, changes to input will be sent back to the Dash server only on enter or when losing focus.
If it's false, it will sent the value back on every change.}

\item{type}{A value equal to: "text", 'number', 'password', 'email', 'range', 'search', 'tel', 'url', 'hidden'. The type of control to render.}

\item{autoComplete}{Character. This attribute indicates whether the value of the control can be automatically completed by the browser.}

\item{autoFocus}{A value equal to: 'autofocus', 'autofocus', 'autofocus' | logical. The element should be automatically focused after the page loaded.
autoFocus is an HTML boolean attribute - it is enabled by a boolean or
'autoFocus'. Alternative capitalizations `autofocus` & `AUTOFOCUS`
are also acccepted.}

\item{disabled}{A value equal to: 'disabled', 'disabled' | logical. If true, the input is disabled and can't be clicked on.
disabled is an HTML boolean attribute - it is enabled by a boolean or
'disabled'. Alternative capitalizations `DISABLED`}

\item{inputMode}{A value equal to: "verbatim", "latin", "latin-name", "latin-prose", "full-width-latin", "kana", "katakana", "numeric", "tel", "email", "url". Provides a hint to the browser as to the type of data that might be
entered by the user while editing the element or its contents.}

\item{list}{Character. Identifies a list of pre-defined options to suggest to the user.
The value must be the id of a <datalist> element in the same document.
The browser displays only options that are valid values for this
input element.
This attribute is ignored when the type attribute's value is
hidden, checkbox, radio, file, or a button type.}

\item{max}{Character | numeric. The maximum (numeric or date-time) value for this item, which must not be less than its minimum (min attribute) value.}

\item{maxLength}{Character | numeric. If the value of the type attribute is text, email, search, password, tel, or url, this attribute specifies the maximum number of characters (in UTF-16 code units) that the user can enter. For other control types, it is ignored. It can exceed the value of the size attribute. If it is not specified, the user can enter an unlimited number of characters. Specifying a negative number results in the default behavior (i.e. the user can enter an unlimited number of characters). The constraint is evaluated only when the value of the attribute has been changed.}

\item{min}{Character | numeric. The minimum (numeric or date-time) value for this item, which must not be greater than its maximum (max attribute) value.}

\item{minLength}{Character | numeric. If the value of the type attribute is text, email, search, password, tel, or url, this attribute specifies the minimum number of characters (in Unicode code points) that the user can enter. For other control types, it is ignored.}

\item{multiple}{Logical. This Boolean attribute indicates whether the user can enter more than one value. This attribute applies when the type attribute is set to email or file, otherwise it is ignored.}

\item{name}{Character. The name of the control, which is submitted with the form data.}

\item{pattern}{Character. A regular expression that the control's value is checked against. The pattern must match the entire value, not just some subset. Use the title attribute to describe the pattern to help the user. This attribute applies when the value of the type attribute is text, search, tel, url, email, or password, otherwise it is ignored. The regular expression language is the same as JavaScript RegExp algorithm, with the 'u' parameter that makes it treat the pattern as a sequence of unicode code points. The pattern is not surrounded by forward slashes.}

\item{placeholder}{Character | numeric. A hint to the user of what can be entered in the control . The placeholder text must not contain carriage returns or line-feeds. Note: Do not use the placeholder attribute instead of a <label> element, their purposes are different. The <label> attribute describes the role of the form element (i.e. it indicates what kind of information is expected), and the placeholder attribute is a hint about the format that the content should take. There are cases in which the placeholder attribute is never displayed to the user, so the form must be understandable without it.}

\item{readOnly}{Logical | a value equal to: 'readonly', 'readonly', 'readonly'. This attribute indicates that the user cannot modify the value of the control. The value of the attribute is irrelevant. If you need read-write access to the input value, do not add the "readonly" attribute. It is ignored if the value of the type attribute is hidden, range, color, checkbox, radio, file, or a button type (such as button or submit).
readOnly is an HTML boolean attribute - it is enabled by a boolean or
'readOnly'. Alternative capitalizations `readonly` & `READONLY`
are also acccepted.}

\item{required}{A value equal to: 'required', 'required' | logical. This attribute specifies that the user must fill in a value before submitting a form. It cannot be used when the type attribute is hidden, image, or a button type (submit, reset, or button). The :optional and :required CSS pseudo-classes will be applied to the field as appropriate.
required is an HTML boolean attribute - it is enabled by a boolean or
'required'. Alternative capitalizations `REQUIRED`
are also acccepted.}

\item{selectionDirection}{Character. The direction in which selection occurred. This is "forward" if the selection was made from left-to-right in an LTR locale or right-to-left in an RTL locale, or "backward" if the selection was made in the opposite direction. On platforms on which it's possible this value isn't known, the value can be "none"; for example, on macOS, the default direction is "none", then as the user begins to modify the selection using the keyboard, this will change to reflect the direction in which the selection is expanding.}

\item{selectionEnd}{Character. The offset into the element's text content of the last selected character. If there's no selection, this value indicates the offset to the character following the current text input cursor position (that is, the position the next character typed would occupy).}

\item{selectionStart}{Character. The offset into the element's text content of the first selected character. If there's no selection, this value indicates the offset to the character following the current text input cursor position (that is, the position the next character typed would occupy).}

\item{size}{Character. The initial size of the control. This value is in pixels unless the value of the type attribute is text or password, in which case it is an integer number of characters. Starting in, this attribute applies only when the type attribute is set to text, search, tel, url, email, or password, otherwise it is ignored. In addition, the size must be greater than zero. If you do not specify a size, a default value of 20 is used.' simply states "the user agent should ensure that at least that many characters are visible", but different characters can have different widths in certain fonts. In some browsers, a certain string with x characters will not be entirely visible even if size is defined to at least x.}

\item{spellCheck}{A value equal to: 'true', 'false' | logical. Setting the value of this attribute to true indicates that the element needs to have its spelling and grammar checked. The value default indicates that the element is to act according to a default behavior, possibly based on the parent element's own spellcheck value. The value false indicates that the element should not be checked.}

\item{step}{Character | numeric. Works with the min and max attributes to limit the increments at which a numeric or date-time value can be set. It can be the string any or a positive floating point number. If this attribute is not set to any, the control accepts only values at multiples of the step value greater than the minimum.}

\item{n_submit}{Numeric. Number of times the `Enter` key was pressed while the input had focus.}

\item{n_submit_timestamp}{Numeric. Last time that `Enter` was pressed.}

\item{n_blur}{Numeric. Number of times the input lost focus.}

\item{n_blur_timestamp}{Numeric. Last time the input lost focus.}

\item{loading_state}{Lists containing elements 'is_loading', 'prop_name', 'component_name'.
those elements have the following types:
  - is_loading (logical; optional): determines if the component is loading or not
  - prop_name (character; optional): holds which property is loading
  - component_name (character; optional): holds the name of the component that is loading. Object that holds the loading state object coming from dash-renderer}

\item{persistence}{Logical | character | numeric. Used to allow user interactions in this component to be persisted when
the component - or the page - is refreshed. If `persisted` is truthy and
hasn't changed from its previous value, a `value` that the user has
changed while using the app will keep that change, as long as
the new `value` also matches what was given originally.
Used in conjunction with `persistence_type`.}

\item{persisted_props}{List of a value equal to: 'value's. Properties whose user interactions will persist after refreshing the
component or the page. Since only `value` is allowed this prop can
normally be ignored.}

\item{persistence_type}{A value equal to: 'local', 'session', 'memory'. Where persisted user changes will be stored:
memory: only kept in memory, reset on page refresh.
local: window.localStorage, data is kept after the browser quit.
session: window.sessionStorage, data is cleared once the browser quit.}
}
