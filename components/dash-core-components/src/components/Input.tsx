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
import {
    HTMLInputTypes,
    InputProps,
    PersistedProps,
    PersistenceTypes,
} from '../types';
import './css/input.css';

const isNumeric = (val: unknown): val is number => fastIsNumeric(val);
const convert = (val: unknown) => (isNumeric(val) ? +val : NaN);

const isEquivalent = (v1: number, v2: number) =>
    v1 === v2 || (isNaN(v1) && isNaN(v2));

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
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    n_blur_timestamp = -1,
    n_submit = 0,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    n_submit_timestamp = -1,
    debounce = false,
    step = 'any',
    autoComplete = 'off',
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persisted_props = [PersistedProps.value],
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
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

            // Count decimal places to avoid floating point precision issues
            const decimalPlaces = (stepAsNum.toString().split('.')[1] || '')
                .length;

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

            // Round to the step's decimal precision
            const roundedValue = parseFloat(
                constrainedValue.toFixed(decimalPlaces)
            );

            input.current.value = roundedValue.toString();
            setValue(roundedValue.toString());
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
        autoComplete,
        disabled: disabledAsBool,
    }) as Pick<InputHTMLAttributes<HTMLInputElement>, HTMLInputProps>;

    const isNumberInput = type === HTMLInputTypes.number;
    const currentNumericValue = parseFloat(String(value ?? 0)) || 0;
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
