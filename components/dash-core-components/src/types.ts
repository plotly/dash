import React from 'react';
import {DashComponent} from '@dash-renderer/types/component';
import ExternalWrapper from '@dash-renderer/wrapper/ExternalWrapper';
import {useDashContext} from '@dash-renderer/wrapper/DashContext';

declare global {
    interface Window {
        dash_component_api: {
            useDashContext: typeof useDashContext;
            ExternalWrapper: typeof ExternalWrapper;
        };
    }
}

export enum PersistenceTypes {
    'local' = 'local',
    'session' = 'session',
    'memory' = 'memory',
}

export enum PersistedProps {
    'value' = 'value',
}

export interface BaseComponentProps<T> {
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id?: string;

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

export interface SliderProps extends BaseComponentProps<SliderProps> {
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
}

export interface RangeSliderProps extends BaseComponentProps<RangeSliderProps> {
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

export interface DropdownProps extends BaseComponentProps<DropdownProps> {
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

export interface ChecklistProps extends BaseComponentProps<ChecklistProps> {
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

export interface RadioItemsProps extends BaseComponentProps<RadioItemsProps> {
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

export interface TextAreaProps extends BaseComponentProps<TextAreaProps> {
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
