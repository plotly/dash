import {pick} from 'ramda';
import React, {
    InputHTMLAttributes,
    KeyboardEvent,
    KeyboardEventHandler,
    useCallback,
    useEffect,
    useRef,
    useState,
} from 'react';
import uniqid from 'uniqid';
import fastIsNumeric from 'fast-isnumeric';
import LoadingElement from '../utils/_LoadingElement';
import {PersistedProps, PersistenceTypes} from '../types';
import './css/input.css';

const isNumeric = (val: unknown): val is number => fastIsNumeric(val);
const convert = (val: unknown) => (isNumeric(val) ? +val : NaN);

const isEquivalent = (v1: number, v2: number) =>
    v1 === v2 || (isNaN(v1) && isNaN(v2));

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

type InputProps = {
    /**
     * The value of the input
     */
    value?: string | number;
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
    /**
     * The class of the input element
     */
    className?: string;
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id?: string;
    /**
     * Dash-assigned callback that gets fired when the value changes.
     */
    setProps: (props: Partial<InputProps>) => void;
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

    /**
     * The type of control to render.
     */
    type?: HTMLInputTypes;
};

const inputProps = [
    'type',
    'placeholder',
    'inputMode',
    'autoComplete',
    'readOnly',
    'required',
    'autoFocus',
    'list',
    'multiple',
    'spellCheck',
    'name',
    'min',
    'max',
    'step',
    'minLength',
    'maxLength',
    'pattern',
    'size',
] as const;

type HTMLInputProps = Extract<
    (typeof inputProps)[number],
    keyof InputHTMLAttributes<HTMLInputElement>
>;

/**
 * A basic HTML input control for entering text, numbers, or passwords.
 *
 * Note that checkbox and radio types are supported through
 * the Checklist and RadioItems component. Dates, times, and file uploads
 * are also supported through separate components.
 */
function Input({
    type = HTMLInputTypes.text,
    inputMode = 'verbatim',
    n_blur = 0,
    n_blur_timestamp = -1,
    n_submit = 0,
    n_submit_timestamp = -1,
    debounce = false,
    step = 'any',
    persisted_props = [PersistedProps.value],
    persistence_type = PersistenceTypes.local,
    disabled,
    ...props
}: InputProps) {
    const input = useRef(document.createElement('input'));
    const [value, setValue] = useState<InputProps['value']>(props.value);
    const [pendingEvent, setPendingEvent] = useState<number>();
    const inputId = useState(() => uniqid('input-'))[0];

    const valprops = type === HTMLInputTypes.number ? {} : {value: value ?? ''};
    let {className} = props;
    className = 'dash-input' + (className ? ` ${className}` : '');

    const setPropValue = useCallback(
        (base: InputProps['value'], value: InputProps['value']) => {
            const {setProps} = props;
            base = convert(base);
            value = input.current.checkValidity() ? convert(value) : NaN;

            if (!isEquivalent(base, value)) {
                setProps({value});
            }
        },
        [props.setProps]
    );

    const onEvent = () => {
        const {value: inputValue} = input.current;
        const valueAsNumber = convert(inputValue);
        if (type === HTMLInputTypes.number) {
            setPropValue(props.value, valueAsNumber ?? value);
        } else {
            const propValue =
                inputValue === '' && props.value === undefined
                    ? undefined
                    : inputValue;
            props.setProps({value: propValue});
        }
        setPendingEvent(undefined);
    };

    const onBlur = useCallback(() => {
        props.setProps({
            n_blur: (n_blur ?? 0) + 1,
            n_blur_timestamp: Date.now(),
        });
        input.current.checkValidity();
        return debounce === true && onEvent();
    }, [n_blur, debounce]);

    const onChange = useCallback(() => {
        const {value} = input.current;
        setValue(value);
    }, []);

    const onKeyPress: KeyboardEventHandler<HTMLInputElement> = useCallback(
        (e: KeyboardEvent) => {
            if (e.key === 'Enter') {
                props.setProps({
                    n_submit: (n_submit ?? 0) + 1,
                    n_submit_timestamp: Date.now(),
                });
            }
            return debounce === true && e.key === 'Enter' && onEvent();
        },
        [n_submit, debounce]
    );

    const setInputValue = useCallback(
        (base: InputProps['value'], value: InputProps['value']) => {
            base = input.current.checkValidity() ? convert(base) : NaN;
            value = convert(value);

            if (!isEquivalent(base, value)) {
                if (typeof value === 'undefined') {
                    input.current.value = '';
                } else {
                    input.current.value = `${value}`;
                }
            }
        },
        []
    );

    const debounceEvent = useCallback(
        (seconds = 0.5) => {
            const {value} = input.current;
            window.clearTimeout(pendingEvent);
            setPendingEvent(
                window.setTimeout(() => {
                    onEvent();
                }, seconds * 1000)
            );

            setValue(value);
        },
        [pendingEvent]
    );

    const handleStepperClick = useCallback(
        (direction: 'increment' | 'decrement') => {
            const currentValue = parseFloat(input.current.value) || 0;
            const stepAsNum = parseFloat(step as string) || 1;
            const newValue =
                direction === 'increment'
                    ? currentValue + stepAsNum
                    : currentValue - stepAsNum;

            // Apply min/max constraints
            let constrainedValue = newValue;
            if (props.min !== undefined) {
                constrainedValue = Math.max(
                    constrainedValue,
                    parseFloat(props.min as string)
                );
            }
            if (props.max !== undefined) {
                constrainedValue = Math.min(
                    constrainedValue,
                    parseFloat(props.max as string)
                );
            }

            input.current.value = constrainedValue.toString();
            setValue(constrainedValue.toString());
            onEvent();
        },
        [step, props.min, props.max, onEvent]
    );

    useEffect(() => {
        const {value} = input.current;
        if (pendingEvent || props.value === value) {
            return;
        }
        const valueAsNumber = convert(value);
        setInputValue(valueAsNumber ?? value, props.value);
        if (type !== HTMLInputTypes.number) {
            setValue(props.value);
        }
    }, [props.value, type, pendingEvent]);

    useEffect(() => {
        // Skip this effect if the value change came from props update (not user input)
        if (value === props.value) {
            return;
        }

        const {selectionStart: cursorPosition} = input.current;
        if (debounce) {
            if (typeof debounce === 'number' && Number.isFinite(debounce)) {
                debounceEvent(debounce);
            }
            if (type !== HTMLInputTypes.number) {
                setTimeout(() => {
                    input.current.setSelectionRange(
                        cursorPosition,
                        cursorPosition
                    );
                }, 0);
            }
        } else {
            onEvent();
        }
    }, [value, debounce, type]);

    const disabledAsBool = [true, 'disabled', 'DISABLED'].includes(
        disabled ?? false
    );

    const pickedInputs = pick(inputProps, {
        ...props,
        type,
        inputMode,
        step,
        disabled: disabledAsBool,
    }) as Pick<InputHTMLAttributes<HTMLInputElement>, HTMLInputProps>;

    const isNumberInput = type === HTMLInputTypes.number;
    const currentNumericValue = convert(input.current.value || '0');
    const minValue = convert(props.min);
    const maxValue = convert(props.max);
    const isDecrementDisabled =
        disabledAsBool || currentNumericValue <= minValue;
    const isIncrementDisabled =
        disabledAsBool || currentNumericValue >= maxValue;

    return (
        <LoadingElement>
            {loadingProps => (
                <div
                    className={`dash-input-container ${className}${
                        type === HTMLInputTypes.hidden
                            ? ' dash-input-hidden'
                            : ''
                    }`.trim()}
                    style={props.style}
                >
                    <input
                        id={props.id || inputId}
                        ref={input}
                        className="dash-input-element"
                        onBlur={onBlur}
                        onChange={onChange}
                        onKeyPress={onKeyPress}
                        {...valprops}
                        {...pickedInputs}
                        {...loadingProps}
                        disabled={disabledAsBool}
                    />
                    {isNumberInput && (
                        <button
                            type="button"
                            className="dash-input-stepper dash-stepper-decrement"
                            onClick={() => handleStepperClick('decrement')}
                            disabled={isDecrementDisabled}
                            aria-controls={props.id || inputId}
                            aria-label="Decrease value"
                        >
                            −
                        </button>
                    )}
                    {isNumberInput && (
                        <button
                            type="button"
                            className="dash-input-stepper dash-stepper-increment"
                            onClick={() => handleStepperClick('increment')}
                            disabled={isIncrementDisabled}
                            aria-controls={props.id || inputId}
                            aria-label="Increase value"
                        >
                            +
                        </button>
                    )}
                </div>
            )}
        </LoadingElement>
    );
}

Input.dashPersistence = {
    persisted_props: [PersistedProps.value],
    persistence_type: PersistenceTypes.local,
};

export default Input;
