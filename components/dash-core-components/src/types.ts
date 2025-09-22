export enum PersistenceTypes {
    'local' = 'local',
    'session' = 'session',
    'memory' = 'memory',
}

export enum PersistedProps {
    'value' = 'value',
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

export interface SliderProps {
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
     * Additional CSS class for the root DOM node
     */
    className?: string;

    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id?: string;

    /**
     * Dash-assigned callback that gets fired when the value or drag_value changes.
     */
    setProps: (props: Partial<SliderProps>) => void;

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

export interface RangeSliderProps {
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
     * Additional CSS class for the root DOM node
     */
    className?: string;

    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id?: string;

    /**
     * Dash-assigned callback that gets fired when the value or drag_value changes.
     */
    setProps: (props: Partial<RangeSliderProps>) => void;

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

export interface TextAreaProps {
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id?: string;

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
    cols?: string | number;

    /**
     * Indicates whether the user can interact with the element.
     */
    disabled?: string | boolean;

    /**
     * Indicates the form that is the owner of the element.
     */
    form?: string;

    /**
     * Defines the maximum number of characters allowed in the element.
     */
    maxLength?: string | number;

    /**
     * Defines the minimum number of characters allowed in the element.
     */
    minLength?: string | number;

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
    rows?: string | number;

    /**
     * Indicates whether the text should be wrapped.
     */
    wrap?: string;

    /**
     * Defines a keyboard shortcut to activate or add focus to the element.
     */
    accessKey?: string;

    /**
     * Often used with CSS to style elements with common properties.
     */
    className?: string;

    /**
     * Indicates whether the element's content is editable.
     */
    contentEditable?: string | boolean;

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
    draggable?: boolean | 'true' | 'false';

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
    spellCheck?: boolean | 'true' | 'false';

    /**
     * Defines CSS styles which will override styles previously set.
     */
    style?: React.CSSProperties;

    /**
     * Overrides the browser's default tab order and follows the one specified instead.
     */
    tabIndex?: string | number;

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

    /**
     * Dash-assigned callback that gets fired when the value changes.
     */
    setProps: (props: Partial<TextAreaProps>) => void;

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
