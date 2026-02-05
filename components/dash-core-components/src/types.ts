import React, {ButtonHTMLAttributes, DetailedHTMLProps} from 'react';
import {BaseDashProps, DashComponent} from '@dash-renderer/types';

export enum PersistenceTypes {
    'local' = 'local',
    'session' = 'session',
    'memory' = 'memory',
}

export enum PersistedProps {
    'value' = 'value',
    'date' = 'date',
    'start_date' = 'start_date',
    'end_date' = 'end_date',
}

export interface BaseDccProps<T>
    extends Pick<BaseDashProps, 'id' | 'componentPath'> {
    /**
     * Additional CSS class for the root DOM node
     */
    className?: string;

    /**
     * Dash-assigned callback that gets fired when component properties change
     */
    setProps: (props: Partial<T>) => void;

    /**
     * Used to allow user interactions in this component to be persisted when
     * the component - or the page - is refreshed. If `persisted` is truthy and
     * hasn't changed from its previous value, a `value` that the user has
     * changed while using the app will keep that change, as long as
     * the new `value` also matches what was given originally.
     * Used in conjunction with `persistence_type`.
     */
    persistence?: boolean | string | number;

    /**
     * Properties whose user interactions will persist after refreshing the
     * component or the page. Since only `value` is allowed this prop can
     * normally be ignored.
     */
    persisted_props?: PersistedProps[];

    /**
     * Where persisted user changes will be stored:
     * memory: only kept in memory, reset on page refresh.
     * local: window.localStorage, data is kept after the browser quit.
     * session: window.sessionStorage, data is cleared once the browser quit.
     */
    persistence_type?: PersistenceTypes;
}

export type ButtonProps = BaseDccProps<ButtonProps> & {
    /**
     * The children of this component.
     */
    children?: React.ReactNode;
    /**
     * Defines the type of the element.
     */
    type?: 'submit' | 'reset' | 'button';
    /**
     * The element should be automatically focused after the page loaded.
     */
    autoFocus?: boolean;
    /**
     * Indicates whether the user can interact with the element.
     */
    disabled?: boolean;
    /**
     * Indicates the form that is the owner of the element.
     */
    form?: string;
    /**
     * Indicates the action of the element, overriding the action defined in the <form>.
     */
    formAction?: string;
    /**
     * If the button/input is a submit button (type="submit"), this attribute sets the encoding type to use during form submission. If this attribute is specified, it overrides the enctype attribute of the button's form owner.
     */
    formEncType?: string;
    /**
     * If the button/input is a submit button (type="submit"), this attribute sets the submission method to use during form submission (GET, POST, etc.). If this attribute is specified, it overrides the method attribute of the button's form owner.
     */
    formMethod?: string;
    /**
     * If the button/input is a submit button (type="submit"), this boolean attribute specifies that the form is not to be validated when it is submitted. If this attribute is specified, it overrides the novalidate attribute of the button's form owner.
     */
    formNoValidate?: boolean;
    /**
     * If the button/input is a submit button (type="submit"), this attribute specifies the browsing context (for example, tab, window, or inline frame) in which to display the response that is received after submitting the form. If this attribute is specified, it overrides the target attribute of the button's form owner.
     */
    formTarget?: string;
    /**
     * Name of the element. For example used by the server to identify the fields in form submits.
     */
    name?: string;
    /**
     * Defines a default value which will be displayed in the element on page load.
     */
    value?: string | string[] | number;
    /**
     * Keyboard shortcut to activate or add focus to the element.
     */
    accessKey?: string;
    /**
     * Indicates whether the element's content is editable.
     */
    contentEditable?: boolean | 'true' | 'false' | 'inherit';
    /**
     * Defines the text direction. Allowed values are ltr (Left-To-Right) or rtl (Right-To-Left).
     */
    dir?: string;
    /**
     * Defines whether the element can be dragged.
     */
    draggable?: boolean;
    /**
     * Prevents rendering of given element, while keeping child elements, e.g. script elements, active.
     */
    hidden?: boolean;
    /**
     * Defines the language used in the element.
     */
    lang?: string;
    /**
     * Defines the role of an element in the context of accessibility.
     */
    role?: string;
    /**
     * Indicates whether spell checking is allowed for the element.
     */
    spellCheck?: boolean;
    /**
     * Defines CSS styles which will override styles previously set.
     */
    style?: React.CSSProperties;
    /**
     * Overrides the browser's default tab order and follows the one specified instead.
     */
    tabIndex?: number;
    /**
     * Text to be displayed in a tooltip when hovering over the element.
     */
    title?: string;
    /**
     * Number of times the button lost focus.
     */
    n_blur?: number;
    /**
     * Last time the button lost focus.
     */
    n_blur_timestamp?: number;
    /**
     * Number of times the button has been clicked.
     */
    n_clicks?: number;
    /**
     * Last time the button was clicked.
     */
    n_clicks_timestamp?: number;
};

export enum HTMLInputTypes {
    // Only allowing the input types with wide browser compatibility
    'text' = 'text',
    'number' = 'number',
    'password' = 'password',
    'email' = 'email',
    'range' = 'range',
    'search' = 'search',
    'tel' = 'tel',
    'url' = 'url',
    'hidden' = 'hidden',
}

export interface InputProps extends BaseDccProps<InputProps> {
    /**
     * The value of the input
     */
    value?: string | number;
    /**
     * The type of control to render.
     */
    type?: HTMLInputTypes;
    /**
     * If true, changes to input will be sent back to the Dash server only on enter or when losing focus.
     * If it's false, it will send the value back on every change.
     * If a number, it will not send anything back to the Dash server until the user has stopped
     * typing for that number of seconds.
     */
    debounce?: boolean | number;
    /**
     * A hint to the user of what can be entered in the control . The placeholder text must not contain carriage returns or line-feeds. Note: Do not use the placeholder attribute instead of a <label> element, their purposes are different. The <label> attribute describes the role of the form element (i.e. it indicates what kind of information is expected), and the placeholder attribute is a hint about the format that the content should take. There are cases in which the placeholder attribute is never displayed to the user, so the form must be understandable without it.
     */
    placeholder?: string | number;
    /**
     * Number of times the `Enter` key was pressed while the input had focus.
     */
    n_submit?: number;
    /**
     * Last time that `Enter` was pressed.
     */
    n_submit_timestamp?: number;
    /**
     * Provides a hint to the browser as to the type of data that might be
     * entered by the user while editing the element or its contents.
     */
    inputMode?: /**
     * Alphanumeric, non-prose content such as usernames and passwords.
     */
    | 'verbatim'
        /**
         * Latin-script input in the user's preferred language with typing aids such as text prediction enabled. For human-to-computer communication such as search boxes.
         */
        | 'latin'
        /**
         * As latin, but for human names.
         */
        | 'latin-name'
        /**
         * As latin, but with more aggressive typing aids. For human-to-human communication such as instant messaging or email.
         */
        | 'latin-prose'
        /**
         * As latin-prose, but for the user's secondary languages.
         */
        | 'full-width-latin'
        /**
         * Kana or romaji input, typically hiragana input, using full-width characters, with support for converting to kanji. Intended for Japanese text input.
         */
        | 'kana'
        /**
         * Katakana input, using full-width characters, with support for converting to kanji. Intended for Japanese text input.
         */
        | 'katakana'
        /**
         * Numeric input, including keys for the digits 0 to 9, the user's preferred thousands separator character, and the character for indicating negative numbers. Intended for numeric codes (e.g. credit card numbers). For actual numbers, prefer using type="number"
         */
        | 'numeric'
        /**
         * Telephone input, including asterisk and pound key. Use type="tel" if possible instead.
         */
        | 'tel'
        /**
         * Email input. Use type="email" if possible instead.
         */
        | 'email'
        /**
         * URL input. Use type="url" if possible instead.
         */
        | 'url';
    /**
     * This attribute indicates whether the value of the control can be automatically completed by the browser.
     */
    autoComplete?: string;
    /**
     * This attribute indicates that the user cannot modify the value of the control. The value of the attribute is irrelevant. If you need read-write access to the input value, do not add the "readonly" attribute. It is ignored if the value of the type attribute is hidden, range, color, checkbox, radio, file, or a button type (such as button or submit).
     * readOnly is an HTML boolean attribute - it is enabled by a boolean or
     * 'readOnly'. Alternative capitalizations `readonly` & `READONLY`
     * are also acccepted.
     */
    readOnly?: boolean | 'readOnly' | 'readonly' | 'READONLY';
    /**
     * This attribute specifies that the user must fill in a value before submitting a form. It cannot be used when the type attribute is hidden, image, or a button type (submit, reset, or button). The :optional and :required CSS pseudo-classes will be applied to the field as appropriate.
     * required is an HTML boolean attribute - it is enabled by a boolean or
     * 'required'. Alternative capitalizations `REQUIRED`
     * are also acccepted.
     */
    required?: boolean | 'required' | 'REQUIRED';
    /**
     * The element should be automatically focused after the page loaded.
     * autoFocus is an HTML boolean attribute - it is enabled by a boolean or
     * 'autoFocus'. Alternative capitalizations `autofocus` & `AUTOFOCUS`
     * are also acccepted.
     */
    autoFocus?: boolean | 'autoFocus' | 'autofocus' | 'AUTOFOCUS';
    /**
     * If true, the input is disabled and can't be clicked on.
     * disabled is an HTML boolean attribute - it is enabled by a boolean or
     * 'disabled'. Alternative capitalizations `DISABLED`
     */
    disabled?: boolean | 'disabled' | 'DISABLED';
    /**
     * Identifies a list of pre-defined options to suggest to the user.
     * The value must be the id of a <datalist> element in the same document.
     * The browser displays only options that are valid values for this
     * input element.
     * This attribute is ignored when the type attribute's value is
     * hidden, checkbox, radio, file, or a button type.
     */
    list?: string;
    /**
     * This Boolean attribute indicates whether the user can enter more than one value. This attribute applies when the type attribute is set to email or file, otherwise it is ignored.
     */
    multiple?: boolean;
    /**
     * Setting the value of this attribute to true indicates that the element needs to have its spelling and grammar checked. The value default indicates that the element is to act according to a default behavior, possibly based on the parent element's own spellcheck value. The value false indicates that the element should not be checked.
     */
    spellCheck?: boolean | 'true' | 'false';
    /**
     * The name of the control, which is submitted with the form data.
     */
    name?: string;
    /**
     * The minimum (numeric or date-time) value for this item, which must not be greater than its maximum (max attribute) value.
     */
    min?: string | number;
    /**
     * The maximum (numeric or date-time) value for this item, which must not be less than its minimum (min attribute) value.
     */
    max?: string | number;
    /**
     * Works with the min and max attributes to limit the increments at which a numeric or date-time value can be set. It can be the string any or a positive floating point number. If this attribute is not set to any, the control accepts only values at multiples of the step value greater than the minimum.
     */
    step?: string | number;
    /**
     * If the value of the type attribute is text, email, search, password, tel, or url, this attribute specifies the minimum number of characters (in Unicode code points) that the user can enter. For other control types, it is ignored.
     */
    minLength?: string | number;
    /**
     * If the value of the type attribute is text, email, search, password, tel, or url, this attribute specifies the maximum number of characters (in UTF-16 code units) that the user can enter. For other control types, it is ignored. It can exceed the value of the size attribute. If it is not specified, the user can enter an unlimited number of characters. Specifying a negative number results in the default behavior (i.e. the user can enter an unlimited number of characters). The constraint is evaluated only when the value of the attribute has been changed.
     */
    maxLength?: string | number;
    /**
     * A regular expression that the control's value is checked against. The pattern must match the entire value, not just some subset. Use the title attribute to describe the pattern to help the user. This attribute applies when the value of the type attribute is text, search, tel, url, email, or password, otherwise it is ignored. The regular expression language is the same as JavaScript RegExp algorithm, with the 'u' parameter that makes it treat the pattern as a sequence of unicode code points. The pattern is not surrounded by forward slashes.
     */
    pattern?: string;
    /**
     * The offset into the element's text content of the first selected character. If there's no selection, this value indicates the offset to the character following the current text input cursor position (that is, the position the next character typed would occupy).
     */
    selectionStart?: string;
    /**
     * The offset into the element's text content of the last selected character. If there's no selection, this value indicates the offset to the character following the current text input cursor position (that is, the position the next character typed would occupy).
     */
    selectionEnd?: string;
    /**
     * The direction in which selection occurred. This is "forward" if the selection was made from left-to-right in an LTR locale or right-to-left in an RTL locale, or "backward" if the selection was made in the opposite direction. On platforms on which it's possible this value isn't known, the value can be "none"; for example, on macOS, the default direction is "none", then as the user begins to modify the selection using the keyboard, this will change to reflect the direction in which the selection is expanding.
     */
    selectionDirection?: string;
    /**
     * Number of times the input lost focus.
     */
    n_blur?: number;
    /**
     * Last time the input lost focus.
     */
    n_blur_timestamp?: number;
    /**
     * The initial size of the control. This value is in pixels unless the value of the type attribute is text or password, in which case it is an integer number of characters. Starting in, this attribute applies only when the type attribute is set to text, search, tel, url, email, or password, otherwise it is ignored. In addition, the size must be greater than zero. If you do not specify a size, a default value of 20 is used.' simply states "the user agent should ensure that at least that many characters are visible", but different characters can have different widths in certain fonts. In some browsers, a certain string with x characters will not be entirely visible even if size is defined to at least x.
     */
    size?: string;
    /**
     * The input's inline styles
     */
    style?: React.CSSProperties;
}

export type SliderMarks = {
    [key: number]: string | {label: string; style?: React.CSSProperties};
};

export type SliderTooltip = {
    /**
     * Determines whether tooltips should always be visible
     * (as opposed to the default, visible on hover)
     */
    always_visible?: boolean;

    /**
     * Determines the placement of tooltips
     * See https://github.com/react-component/tooltip#api
     * top/bottom{*} sets the _origin_ of the tooltip, so e.g. `topLeft`
     * will in reality appear to be on the top right of the handle
     */
    placement?:
        | 'left'
        | 'right'
        | 'top'
        | 'bottom'
        | 'topLeft'
        | 'topRight'
        | 'bottomLeft'
        | 'bottomRight';

    /**
     * Template string to display the tooltip in.
     * Must contain `{value}`, which will be replaced with either
     * the default string representation of the value or the result of the
     * transform function if there is one.
     */
    template?: string;

    /**
     * Custom style for the tooltip.
     */
    style?: React.CSSProperties;

    /**
     * Reference to a function in the `window.dccFunctions` namespace.
     * This can be added in a script in the asset folder.
     *
     * For example, in `assets/tooltip.js`:
     * ```
     * window.dccFunctions = window.dccFunctions || {};
     * window.dccFunctions.multByTen = function(value) {
     *     return value * 10;
     * }
     * ```
     * Then in the component `tooltip={'transform': 'multByTen'}`
     */
    transform?: string;
};

export interface SliderProps extends BaseDccProps<SliderProps> {
    /**
     * Minimum allowed value of the slider
     */
    min?: number;

    /**
     * Maximum allowed value of the slider
     */
    max?: number;

    /**
     * Value by which increments or decrements are made
     */
    step?: number | null;

    /**
     * Marks on the slider.
     * The key determines the position (a number),
     * and the value determines what will show.
     * If you want to set the style of a specific mark point,
     * the value should be an object which
     * contains style and label properties.
     */
    marks?: SliderMarks | null;

    /**
     * The value of the input
     */
    value?: number | null;

    /**
     * The value of the input during a drag
     */
    drag_value?: number;

    /**
     * If true, the handles can't be moved.
     */
    disabled?: boolean;

    /**
     * When the step value is greater than 1,
     * you can set the dots to true if you want to
     * render the slider with dots.
     */
    dots?: boolean;

    /**
     * If the value is true, it means a continuous
     * value is included. Otherwise, it is an independent value.
     */
    included?: boolean;

    /**
     * If the value is true, the slider is rendered in reverse.
     */
    reverse?: boolean;

    /**
     * Configuration for tooltips describing the current slider value
     */
    tooltip?: SliderTooltip;

    /**
     * Determines when the component should update its `value`
     * property. If `mouseup` (the default) then the slider
     * will only trigger its value when the user has finished
     * dragging the slider. If `drag`, then the slider will
     * update its value continuously as it is being dragged.
     * If you want different actions during and after drag,
     * leave `updatemode` as `mouseup` and use `drag_value`
     * for the continuously updating value.
     */
    updatemode?: 'mouseup' | 'drag';

    /**
     * If true, the slider will be vertical
     */
    vertical?: boolean;

    /**
     * The height, in px, of the slider if it is vertical.
     */
    verticalHeight?: number;

    /**
     * If false, the input elements for directly entering values will be hidden.
     * Only the slider will be visible and it will occupy 100% width of the container.
     */
    allow_direct_input?: boolean;
}

export interface RangeSliderProps extends BaseDccProps<RangeSliderProps> {
    /**
     * Minimum allowed value of the slider
     */
    min?: number;

    /**
     * Maximum allowed value of the slider
     */
    max?: number;

    /**
     * Value by which increments or decrements are made
     */
    step?: number | null;

    /**
     * Marks on the slider.
     * The key determines the position (a number),
     * and the value determines what will show.
     * If you want to set the style of a specific mark point,
     * the value should be an object which
     * contains style and label properties.
     */
    marks?: SliderMarks | null;

    /**
     * The value of the input
     */
    value?: number[] | null;

    /**
     * The value of the input during a drag
     */
    drag_value?: number[];

    /**
     * allowCross could be set as true to allow those handles to cross.
     */
    allowCross?: boolean;

    /**
     * pushable could be set as true to allow pushing of
     * surrounding handles when moving an handle.
     * When set to a number, the number will be the
     * minimum ensured distance between handles.
     */
    pushable?: boolean | number;

    /**
     * If true, the handles can't be moved.
     */
    disabled?: boolean;

    /**
     * Determine how many ranges to render, and multiple handles
     * will be rendered (number + 1).
     */
    count?: number;

    /**
     * When the step value is greater than 1,
     * you can set the dots to true if you want to
     * render the slider with dots.
     */
    dots?: boolean;

    /**
     * If the value is true, it means a continuous
     * value is included. Otherwise, it is an independent value.
     */
    included?: boolean;

    /**
     * If the value is true, the slider is rendered in reverse.
     */
    reverse?: boolean;

    /**
     * Configuration for tooltips describing the current slider values
     */
    tooltip?: SliderTooltip;

    /**
     * Determines when the component should update its `value`
     * property. If `mouseup` (the default) then the slider
     * will only trigger its value when the user has finished
     * dragging the slider. If `drag`, then the slider will
     * update its value continuously as it is being dragged.
     * Note that for the latter case, the `drag_value`
     * property could be used instead.
     */
    updatemode?: 'mouseup' | 'drag';

    /**
     * If true, the slider will be vertical
     */
    vertical?: boolean;

    /**
     * The height, in px, of the slider if it is vertical.
     */
    verticalHeight?: number;

    /**
     * If false, the input elements for directly entering values will be hidden.
     * Only the slider will be visible and it will occupy 100% width of the container.
     */
    allow_direct_input?: boolean;
}

export type OptionValue = string | number | boolean;

export type DetailedOption = {
    label: string | DashComponent | DashComponent[];
    /**
     * The value of the option. This value
     * corresponds to the items specified in the
     * `value` property.
     */
    value: OptionValue;
    /**
     * If true, this option is disabled and cannot be selected.
     */
    disabled?: boolean;
    /**
     * The HTML 'title' attribute for the option. Allows for
     * information on hover. For more information on this attribute,
     * see https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/title
     */
    title?: string;
    /**
     * Optional search value for the option, to use if the label
     * is a component or provide a custom search value different
     * from the label. If no search value and the label is a
     * component, the `value` will be used for search.
     */
    search?: string;
};

/**
 * Array of options where the label and the value are the same thing, or an option dict
 */
export type OptionsArray = (OptionValue | DetailedOption)[];

/**
 * Simpler `options` representation in dictionary format. The order is not guaranteed.
 * {`value1`: `label1`, `value2`: `label2`, ... }
 * which is equal to
 * [{label: `label1`, value: `value1`}, {label: `label2`, value: `value2`}, ...]
 */
export type OptionsDict = Record<string, string>;

export interface DropdownProps extends BaseDccProps<DropdownProps> {
    /**
     * An array of options {label: [string|number], value: [string|number]},
     * an optional disabled field can be used for each option
     */
    options?: OptionsArray | OptionsDict;

    /**
     * The value of the input. If `multi` is false (the default)
     * then value is just a string that corresponds to the values
     * provided in the `options` property. If `multi` is true, then
     * multiple values can be selected at once, and `value` is an
     * array of items with values corresponding to those in the
     * `options` prop.
     */
    value?: OptionValue | OptionValue[] | null;

    /**
     * If true, the user can select multiple values
     */
    multi?: boolean;

    /**
     * Whether or not the dropdown is "clearable", that is, whether or
     * not a small "x" appears on the right of the dropdown that removes
     * the selected value.
     */
    clearable?: boolean;

    /**
     * Whether to enable the searching feature or not
     */
    searchable?: boolean;

    /**
     * The value typed in the DropDown for searching.
     */
    search_value?: string;

    /**
     * The grey, default text shown when no option is selected
     */
    placeholder?: string;

    /**
     * If true, this dropdown is disabled and the selection cannot be changed.
     */
    disabled?: boolean;

    /**
     * If false, the menu of the dropdown will not close once a value is selected.
     */
    closeOnSelect?: boolean;

    /**
     * height of each option. Can be increased when label lengths would wrap around
     */
    optionHeight?: 'auto' | number;

    /**
     * height of the options dropdown.
     */
    maxHeight?: number;

    /**
     * Defines CSS styles which will override styles previously set.
     */
    style?: React.CSSProperties;

    /**
     * Text for customizing the labels rendered by this component.
     */
    labels?: {
        select_all?: string;
        deselect_all?: string;
        selected_count?: string;
        search?: string;
        clear_search?: string;
        clear_selection?: string;
        no_options_found?: string;
    };
}

export interface ChecklistProps extends BaseDccProps<ChecklistProps> {
    /**
     * An array of options
     */
    options?: OptionsArray | OptionsDict;

    /**
     * The currently selected value
     */
    value?: OptionValue[] | null;

    /**
     * Indicates whether the options labels should be displayed inline (true=horizontal)
     * or in a block (false=vertical).
     */
    inline?: boolean;

    /**
     * The style of the container (div)
     */
    style?: React.CSSProperties;

    /**
     * The style of the <input> checkbox element
     */
    inputStyle?: React.CSSProperties;

    /**
     * The class of the <input> checkbox element
     */
    inputClassName?: string;

    /**
     * The style of the <label> that wraps the checkbox input
     *  and the option's label
     */
    labelStyle?: React.CSSProperties;

    /**
     * The class of the <label> that wraps the checkbox input
     *  and the option's label
     */
    labelClassName?: string;
}

export interface RadioItemsProps extends BaseDccProps<RadioItemsProps> {
    /**
     * An array of options
     */
    options?: OptionsArray | OptionsDict;

    /**
     * The currently selected value
     */
    value?: OptionValue | null;

    /**
     * Indicates whether the options labels should be displayed inline (true=horizontal)
     * or in a block (false=vertical).
     */
    inline?: boolean;

    /**
     * The style of the container (div)
     */
    style?: React.CSSProperties;

    /**
     * The style of the <input> checkbox element
     */
    inputStyle?: React.CSSProperties;

    /**
     * The class of the <input> checkbox element
     */
    inputClassName?: string;

    /**
     * The style of the <label> that wraps the checkbox input
     *  and the option's label
     */
    labelStyle?: React.CSSProperties;

    /**
     * The class of the <label> that wraps the checkbox input
     *  and the option's label
     */
    labelClassName?: string;
}

export interface TextAreaProps extends BaseDccProps<TextAreaProps> {
    /**
     * The value of the textarea
     */
    value?: string;

    /**
     * The element should be automatically focused after the page loaded.
     */
    autoFocus?: string;

    /**
     * Defines the number of columns in a textarea.
     */
    cols?: number;

    /**
     * Indicates whether the user can interact with the element.
     */
    disabled?: boolean | 'disabled' | 'DISABLED';

    /**
     * Indicates the form that is the owner of the element.
     */
    form?: string;

    /**
     * Defines the maximum number of characters allowed in the element.
     */
    maxLength?: number;

    /**
     * Defines the minimum number of characters allowed in the element.
     */
    minLength?: number;

    /**
     * Name of the element. For example used by the server to identify the fields in form submits.
     */
    name?: string;

    /**
     * Provides a hint to the user of what can be entered in the field.
     */
    placeholder?: string;

    /**
     * Indicates whether the element can be edited.
     * readOnly is an HTML boolean attribute - it is enabled by a boolean or
     * 'readOnly'. Alternative capitalizations `readonly` & `READONLY`
     * are also acccepted.
     */
    readOnly?: boolean | 'readOnly' | 'readonly' | 'READONLY';

    /**
     * Indicates whether this element is required to fill out or not.
     * required is an HTML boolean attribute - it is enabled by a boolean or
     * 'required'. Alternative capitalizations `REQUIRED`
     * are also acccepted.
     */
    required?: boolean | 'required' | 'REQUIRED';

    /**
     * Defines the number of rows in a text area.
     */
    rows?: number;

    /**
     * Indicates whether the text should be wrapped.
     */
    wrap?: string;

    /**
     * Defines a keyboard shortcut to activate or add focus to the element.
     */
    accessKey?: string;

    /**
     * Indicates whether the element's content is editable.
     */
    contentEditable?: boolean;

    /**
     * Defines the ID of a <menu> element which will serve as the element's context menu.
     */
    contextMenu?: string;

    /**
     * Defines the text direction. Allowed values are ltr (Left-To-Right) or rtl (Right-To-Left)
     */
    dir?: string;

    /**
     * Defines whether the element can be dragged.
     */
    draggable?: boolean;

    /**
     * Prevents rendering of given element, while keeping child elements, e.g. script elements, active.
     */
    hidden?: string;

    /**
     * Defines the language used in the element.
     */
    lang?: string;

    /**
     * Indicates whether spell checking is allowed for the element.
     */
    spellCheck?: boolean;

    /**
     * Defines CSS styles which will override styles previously set.
     */
    style?: React.CSSProperties;

    /**
     * Overrides the browser's default tab order and follows the one specified instead.
     */
    tabIndex?: number;

    /**
     * Text to be displayed in a tooltip when hovering over the element.
     */
    title?: string;

    /**
     * Number of times the textarea lost focus.
     */
    n_blur?: number;
    /**
     * Last time the textarea lost focus.
     */
    n_blur_timestamp?: number;

    /**
     * Number of times the textarea has been clicked.
     */
    n_clicks?: number;
    /**
     * Last time the textarea was clicked.
     */
    n_clicks_timestamp?: number;
}

export interface TooltipProps {
    /**
     * The contents of the tooltip
     */
    children?: React.ReactNode;

    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id?: string;

    /**
     * The class of the tooltip
     */
    className?: string;

    /**
     * The style of the tooltip
     */
    style?: React.CSSProperties;

    /**
     * The bounding box coordinates of the item to label, in px relative to
     * the positioning parent of the Tooltip component.
     */
    bbox?: {
        x0: number;
        y0: number;
        x1: number;
        y1: number;
    };

    /**
     * Whether to show the tooltip
     */
    show?: boolean;

    /**
     * The side of the `bbox` on which the tooltip should open.
     */
    direction?: 'top' | 'right' | 'bottom' | 'left';

    /**
     * Color of the tooltip border, as a CSS color string.
     */
    border_color?: string;

    /**
     * Color of the tooltip background, as a CSS color string.
     */
    background_color?: string;

    /**
     * The text displayed in the tooltip while loading
     */
    loading_text?: string;

    /**
     * The `z-index` CSS property to assign to the tooltip. Components with
     * higher values will be displayed on top of components with lower values.
     */
    zindex?: number;

    /**
     * Whether the tooltip itself can be targeted by pointer events.
     * For tooltips triggered by hover events, typically this should be left
     * `false` to avoid the tooltip interfering with those same events.
     */
    targetable?: boolean;

    /**
     * Dash-assigned callback that gets fired when the value changes.
     */
    setProps: (props: Partial<TooltipProps>) => void;
}

export interface LoadingProps extends BaseDccProps<LoadingProps> {
    /**
     * Array that holds components to render
     */
    children?: React.ReactNode;

    /**
     * Property that determines which built-in spinner to show
     * one of 'graph', 'cube', 'circle', 'dot', or 'default'.
     */
    type?: 'graph' | 'cube' | 'circle' | 'dot' | 'default';

    /**
     * Boolean that makes the built-in spinner display full-screen
     */
    fullscreen?: boolean;

    /**
     * If true, the built-in spinner will display the component_name and prop_name
     * while loading
     */
    debug?: boolean;

    /**
     * Additional CSS styling for the built-in spinner root DOM node
     */
    style?: React.CSSProperties;

    /**
     *  Additional CSS class for the outermost dcc.Loading parent div DOM node
     */
    parent_className?: string;

    /**
     * Additional CSS styling for the outermost dcc.Loading parent div DOM node
     */
    parent_style?: React.CSSProperties;
    /**
     * Additional CSS styling for the spinner overlay. This is applied to the
     * dcc.Loading children while the spinner is active.  The default is `{'visibility': 'hidden'}`
     */
    overlay_style?: React.CSSProperties;

    /**
     * Primary color used for the built-in loading spinners
     */
    color?: string;

    /**
     * Setting display to  "show" or "hide"  will override the loading state coming from dash-renderer
     */
    display?: 'auto' | 'show' | 'hide';

    /**
     * Add a time delay (in ms) to the spinner being removed to prevent flickering.
     */
    delay_hide?: number;

    /**
     * Add a time delay (in ms) to the spinner being shown after the loading_state
     * is set to True.
     */
    delay_show?: number;

    /**
     * Whether the Spinner should show on app start-up before the loading state
     * has been determined. Default True.  Use when also setting `delay_show`.
     */
    show_initially?: boolean;

    /**
     * Specify component and prop to trigger showing the loading spinner
     * example: `{"output-container": "children", "grid": ["rowData", "columnDefs]}`
     *
     */
    target_components?: Record<string, string | string[]>;

    /**
     *  Component to use rather than the built-in spinner specified in the `type` prop.
     *
     */
    custom_spinner?: React.ReactNode;
}

export interface TabsProps extends BaseDccProps<TabsProps> {
    /**
     * The value of the currently selected Tab
     */
    value?: string;

    /**
     * Appends a class to the Tab content container holding the children of the Tab that is selected.
     */
    content_className?: string;

    /**
     * Appends a class to the top-level parent container holding both the Tabs container and the content container.
     */
    parent_className?: string;

    /**
     * Appends (inline) styles to the Tabs container holding the individual Tab components.
     */
    style?: React.CSSProperties;

    /**
     * Appends (inline) styles to the top-level parent container holding both the Tabs container and the content container.
     */
    parent_style?: React.CSSProperties;

    /**
     * Appends (inline) styles to the tab content container holding the children of the Tab that is selected.
     */
    content_style?: React.CSSProperties;

    /**
     * Renders the tabs vertically (on the side)
     */
    vertical?: boolean;

    /**
     * Breakpoint at which tabs are rendered full width (can be 0 if you don't want full width tabs on mobile)
     */
    mobile_breakpoint?: number;

    /**
     * Array that holds Tab components
     */
    children?: DashComponent;

    /**
     * Holds the colors used by the Tabs and Tab components. If you set these, you should specify colors for all properties, so:
     * colors: {
     *    border: '#d6d6d6',
     *    primary: '#1975FA',
     *    background: '#f9f9f9'
     *  }
     */
    colors?: {
        border: string;
        primary: string;
        background: string;
    };
}

// Note a quirk in how this extends the BaseDccProps: `setProps` is shared
// with `TabsProps` (plural!) due to how tabs are implemented. This is
// intentional.
export interface TabProps extends BaseDccProps<TabsProps> {
    /**
     * The tab's label
     */
    label?: string | DashComponent;

    /**
     * The content of the tab - will only be displayed if this tab is selected
     */
    children?: DashComponent;

    /**
     * Value for determining which Tab is currently selected
     */
    value?: string;

    /**
     * Determines if tab is disabled or not - defaults to false
     */
    disabled?: boolean;

    /**
     * Overrides the default (inline) styles when disabled
     */
    disabled_style?: React.CSSProperties;

    /**
     * Appends a class to the Tab component when it is disabled.
     */
    disabled_className?: string;

    /**
     * Appends a class to the Tab component.
     */
    className?: string;

    /**
     * Appends a class to the Tab component when it is selected.
     */
    selected_className?: string;

    /**
     * Overrides the default (inline) styles for the Tab component.
     */
    style?: React.CSSProperties;

    /**
     * Overrides the default (inline) styles for the Tab component when it is selected.
     */
    selected_style?: React.CSSProperties;

    /**
     * A custom width for this tab, in the format of `50px` or `50%`; numbers
     * are treated as pixel values. By default, there is no width and this Tab
     * is evenly spaced along with all the other tabs to occupy the available
     * space. Setting this value will "fix" this tab width to the given size.
     * while the other "non-fixed" tabs will continue to automatically
     * occupying the remaining available space.
     * This property has no effect when tabs are displayed vertically.
     */
    width?: string | number;
}

export enum DayOfWeek {
    Sunday = 0,
    Monday = 1,
    Tuesday = 2,
    Wednesday = 3,
    Thursday = 4,
    Friday = 5,
    Saturday = 6,
}

export enum CalendarDirection {
    LeftToRight = 'ltr',
    RightToLeft = 'rtl',
}

export interface DatePickerSingleProps
    extends BaseDccProps<DatePickerSingleProps> {
    /**
     * Specifies the starting date for the component, best practice is to pass
     * value via datetime object
     */
    date?: `${string}-${string}-${string}`;

    /**
     * Specifies the lowest selectable date for the component.
     * Accepts datetime.datetime objects or strings
     * in the format 'YYYY-MM-DD'
     */
    min_date_allowed?: string;

    /**
     * Specifies the highest selectable date for the component.
     * Accepts datetime.datetime objects or strings
     * in the format 'YYYY-MM-DD'
     */
    max_date_allowed?: string;

    /**
     * Specifies additional days between min_date_allowed and max_date_allowed
     * that should be disabled. Accepted datetime.datetime objects or strings
     * in the format 'YYYY-MM-DD'
     */
    disabled_days?: string[];

    /**
     * Text that will be displayed in the input
     * box of the date picker when no date is selected.
     */
    placeholder?: string;

    /**
     * Specifies the month that is initially presented when the user
     * opens the calendar. Accepts datetime.datetime objects or strings
     * in the format 'YYYY-MM-DD'
     *
     */
    initial_visible_month?: string;

    /**
     * Whether or not the dropdown is "clearable", that is, whether or
     * not a small "x" appears on the right of the dropdown that removes
     * the selected value.
     */
    clearable?: boolean;

    /**
     * If True, the calendar will automatically open when cleared
     */
    reopen_calendar_on_clear?: boolean;

    /**
     * Specifies the format that the selected dates will be displayed
     * valid formats are variations of "MM YY DD". For example:
     * "MM YY DD" renders as '05 10 97' for May 10th 1997
     * "MMMM, YY" renders as 'May, 1997' for May 10th 1997
     * "M, D, YYYY" renders as '07, 10, 1997' for September 10th 1997
     * "MMMM" renders as 'May' for May 10 1997
     */
    display_format?: string;

    /**
     * Specifies the format that the month will be displayed in the calendar,
     * valid formats are variations of "MM YY". For example:
     * "MM YY" renders as '05 97' for May 1997
     * "MMMM, YYYY" renders as 'May, 1997' for May 1997
     * "MMM, YY" renders as 'Sep, 97' for September 1997
     */
    month_format?: string;

    /**
     * Specifies what day is the first day of the week, values must be
     * from [0, ..., 6] with 0 denoting Sunday and 6 denoting Saturday
     */
    first_day_of_week?: DayOfWeek;

    /**
     * If True the calendar will display days that rollover into
     * the next month
     */
    show_outside_days?: boolean;

    /**
     * If True the calendar will not close when the user has selected a value
     * and will wait until the user clicks off the calendar
     */
    stay_open_on_select?: boolean;

    /**
     * Orientation of calendar, either vertical or horizontal.
     * Valid options are 'vertical' or 'horizontal'.
     */
    calendar_orientation?: 'vertical' | 'horizontal';

    /**
     * Number of calendar months that are shown when calendar is opened
     */
    number_of_months_shown?: number;

    /**
     * If True, calendar will open in a screen overlay portal,
     * not supported on vertical calendar
     */
    with_portal?: boolean;

    /**
     * If True, calendar will open in a full screen overlay portal, will
     * take precedent over 'withPortal' if both are set to True,
     * not supported on vertical calendar
     */
    with_full_screen_portal?: boolean;

    /**
     * Size of rendered calendar days, higher number
     * means bigger day size and larger calendar overall
     */
    day_size?: number;

    /**
     * Determines whether the calendar and days operate
     * from left to right or from right to left
     */
    is_RTL?: boolean;

    /**
     * If True, no dates can be selected.
     */
    disabled?: boolean;

    /**
     * CSS styles appended to wrapper div
     */
    style?: React.CSSProperties;
}

export interface DatePickerRangeProps
    extends Omit<DatePickerSingleProps, 'date'> {
    /**
     * Specifies the starting date for the component.
     * Accepts datetime.datetime objects or strings
     * in the format 'YYYY-MM-DD'
     */
    start_date?: `${string}-${string}-${string}`;

    /**
     * Specifies the ending date for the component.
     * Accepts datetime.datetime objects or strings
     * in the format 'YYYY-MM-DD'
     */
    end_date?: `${string}-${string}-${string}`;

    /**
     * Specifies a minimum number of nights that must be selected between
     * the startDate and the endDate
     */
    minimum_nights?: number;

    /**
     * Determines when the component should update
     * its value. If `bothdates`, then the DatePicker
     * will only trigger its value when the user has
     * finished picking both dates. If `singledate`, then
     * the DatePicker will update its value
     * as one date is picked.
     */
    updatemode?: 'singledate' | 'bothdates';

    /**
     * Text that will be displayed in the first input
     * box of the date picker when no date is selected. Default value is 'Start Date'
     */
    start_date_placeholder_text?: string;

    /**
     * Text that will be displayed in the second input
     * box of the date picker when no date is selected. Default value is 'End Date'
     */
    end_date_placeholder_text?: string;

    /**
     * The HTML element ID of the start date input field.
     * Not used by Dash, only by CSS.
     */
    start_date_id?: string;

    /**
     * The HTML element ID of the end date input field.
     * Not used by Dash, only by CSS.
     */
    end_date_id?: string;

    setProps: (props: Partial<DatePickerRangeProps>) => void;
}
