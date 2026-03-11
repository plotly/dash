import React, {
    forwardRef,
    memo,
    useCallback,
    useImperativeHandle,
    useLayoutEffect,
    useMemo,
    useRef,
    useState,
} from 'react';
import {append, includes, without} from 'ramda';
import {VariableSizeList, ListChildComponentProps} from 'react-window';
import {DetailedOption, OptionValue} from 'src/types';
import '../components/css/optionslist.css';

const DEFAULT_ITEM_HEIGHT = 35;

interface StylingProps {
    id?: string;
    className?: string;
    style?: React.CSSProperties;
    optionClassName?: string;
    optionStyle?: React.CSSProperties;
    inputType?: 'checkbox' | 'radio';
    inputClassName?: string;
    inputStyle?: React.CSSProperties;
    labelClassName?: string;
    labelStyle?: React.CSSProperties;
}

interface OptionLabelProps extends DetailedOption {
    index: string | number;
}

export const OptionLabel: React.FC<OptionLabelProps> = ({
    index,
    label,
    title,
    value,
}) => {
    const ctx = window.dash_component_api.useDashContext();
    const ExternalWrapper = window.dash_component_api.ExternalWrapper;

    if (typeof label === 'object') {
        const labels = label instanceof Array ? label : [label];
        return (
            <>
                {labels.map((label, i) => (
                    <ExternalWrapper
                        key={i}
                        component={label}
                        componentPath={[...ctx.componentPath, index, i]}
                    />
                ))}
            </>
        );
    }

    const displayLabel = `${label ?? value}`;
    return <span title={title}>{displayLabel}</span>;
};

interface OptionProps extends StylingProps {
    index: number;
    option: DetailedOption;
    isSelected: boolean;
    onChange: (option: DetailedOption) => void;
}

export const Option: React.FC<OptionProps> = ({
    option,
    isSelected,
    onChange,
    optionClassName,
    optionStyle,
    inputType = 'checkbox',
    inputClassName,
    inputStyle,
    labelClassName,
    labelStyle,
    index,
    id,
}) => {
    const classNames = [
        'dash-options-list-option',
        isSelected ? 'selected' : '',
        optionClassName,
    ].filter(Boolean);

    const inputClassNames = [
        'dash-options-list-option-checkbox',
        inputClassName,
    ].filter(Boolean);

    const labelClassNames = [
        'dash-options-list-option-text',
        labelClassName,
    ].filter(Boolean);

    return (
        <label
            className={classNames.join(' ')}
            role="option"
            aria-selected={isSelected}
            style={optionStyle}
            data-option-index={index}
        >
            <span className="dash-options-list-option-wrapper">
                <input
                    type={inputType}
                    checked={isSelected}
                    name={id}
                    value={
                        typeof option.value === 'boolean'
                            ? `${option.value}`
                            : option.value
                    }
                    disabled={!!option.disabled}
                    onChange={() => onChange(option)}
                    onKeyUp={e => {
                        if (e.key === 'Enter') {
                            onChange(option);
                        }
                    }}
                    readOnly
                    className={inputClassNames.join(' ')}
                    style={inputStyle}
                />
            </span>
            <span
                className={labelClassNames.join(' ')}
                style={labelStyle}
                title={option.title}
            >
                <OptionLabel {...option} index={index} />
            </span>
        </label>
    );
};

interface RowData {
    options: DetailedOption[];
    selected: OptionValue[];
    onChange: (option: DetailedOption) => void;
    passThruProps: StylingProps;
    setOptionHeight: (index: number, height: number) => void;
}

const Row = memo(({index, style, data}: ListChildComponentProps<RowData>) => {
    const {options, selected, onChange, passThruProps, setOptionHeight} = data;
    const option = options[index];
    const isSelected = includes(option.value, selected);

    return (
        <div style={style}>
            <div
                ref={el =>
                    el &&
                    setOptionHeight(index, el.getBoundingClientRect().height)
                }
            >
                <Option
                    id={passThruProps.id}
                    index={index}
                    option={option}
                    isSelected={isSelected}
                    onChange={onChange}
                    {...passThruProps}
                />
            </div>
        </div>
    );
});

Row.displayName = 'Row';

export interface OptionsListHandle {
    scrollToItem: (index: number) => void;
    focusItem: (index: number) => void;
}

interface OptionsListProps extends StylingProps {
    options: DetailedOption[];
    selected: OptionValue[];
    onSelectionChange: (selected: OptionValue[]) => void;
    optionHeight?: number;
    maxHeight?: number;
}

export const OptionsList = forwardRef<OptionsListHandle, OptionsListProps>(
    (
        {
            options,
            selected,
            onSelectionChange,
            optionHeight,
            maxHeight = window.innerHeight,
            id,
            className,
            style,
            ...passThruProps
        },
        ref
    ) => {
        const listRef = useRef<VariableSizeList>(null);
        const containerRef = useRef<HTMLDivElement>(null);
        const pendingFocusRef = useRef<number | null>(null);
        const heightsRef = useRef<Map<number, number>>(new Map());
        const [measuredHeight, setMeasuredHeight] = useState<number | null>(
            null
        );

        const defaultOptionHeight = optionHeight ?? DEFAULT_ITEM_HEIGHT;

        const getOptionHeight = useCallback(
            (index: number): number =>
                heightsRef.current.get(index) ?? defaultOptionHeight,
            [defaultOptionHeight]
        );

        const setOptionHeight = useCallback((index: number, height: number) => {
            if (heightsRef.current.get(index) !== height) {
                heightsRef.current.set(index, height);
                listRef.current?.resetAfterIndex(index, false);
            }
        }, []);

        // Measure container height before first paint. Row measureRefs
        // have already fired, so invalidate the list's internal cache
        // so the re-render picks up measured heights.
        useLayoutEffect(() => {
            const el = containerRef.current;
            if (!el || measuredHeight !== null) {
                return;
            }
            listRef.current?.resetAfterIndex(0, false);
            const h = el.getBoundingClientRect().height;
            if (h > 0) {
                setMeasuredHeight(h);
            }
        }, []);

        const defaultListHeight = options.length * defaultOptionHeight;
        const listHeight =
            measuredHeight === null
                ? maxHeight
                : Math.min(measuredHeight, defaultListHeight);

        const focusOption = useCallback((optionIndex: number) => {
            requestAnimationFrame(() => {
                if (pendingFocusRef.current !== optionIndex) {
                    return;
                }
                const deferred = containerRef.current?.querySelector(
                    `[data-option-index="${optionIndex}"] input`
                );
                if (deferred instanceof HTMLElement) {
                    pendingFocusRef.current = null;
                    deferred.focus();
                }
            });
        }, []);

        useImperativeHandle(ref, () => ({
            scrollToItem: (index: number) => {
                if (listRef.current) {
                    listRef.current.scrollToItem(index, 'smart');
                }
            },
            focusItem: (index: number) => {
                pendingFocusRef.current = index;
                if (listRef.current) {
                    listRef.current.scrollToItem(index, 'center');
                }
                focusOption(index);
            },
        }));

        const handleChange = useCallback(
            (option: DetailedOption) => {
                let newValue: OptionValue[];
                if (includes(option.value, selected)) {
                    newValue = without([option.value], selected);
                } else {
                    newValue = append(option.value, selected);
                }
                onSelectionChange(newValue);
            },
            [selected, onSelectionChange]
        );

        const classNames = ['dash-options-list', className].filter(Boolean);

        const handleItemsRendered = useCallback(() => {
            if (typeof pendingFocusRef.current === 'number') {
                focusOption(pendingFocusRef.current);
            }
        }, []);

        // Render the longest-label option (sampled) for intrinsic width.
        const sizerDiv = useMemo(() => {
            if (!options.length) {
                return null;
            }
            const step = Math.max(1, Math.floor(options.length / 100));
            let longestOption = options[0];
            let maxLen = 0;
            for (let i = 0; i < options.length; i += step) {
                const {label} = options[i];
                if (typeof label !== 'string') {
                    return null;
                }
                if (label.length > maxLen) {
                    longestOption = options[i];
                    maxLen = label.length;
                }
            }
            return (
                <Option
                    index={-1}
                    option={longestOption}
                    isSelected={false}
                    // eslint-disable-next-line @typescript-eslint/no-empty-function
                    onChange={() => {}}
                />
            );
        }, [options]);

        const itemData = useMemo<RowData>(
            () => ({
                options,
                selected,
                onChange: handleChange,
                passThruProps: {id, ...passThruProps},
                setOptionHeight,
            }),
            [options, selected, handleChange, id, passThruProps]
        );

        return (
            <div
                ref={containerRef}
                id={id}
                className={classNames.join(' ')}
                style={style}
                role="listbox"
            >
                <VariableSizeList
                    ref={listRef}
                    height={listHeight}
                    itemCount={options.length}
                    itemSize={getOptionHeight}
                    estimatedItemSize={defaultOptionHeight}
                    width="100%"
                    className="dash-options-list-virtualized"
                    onItemsRendered={handleItemsRendered}
                    itemData={itemData}
                >
                    {Row}
                </VariableSizeList>
                {sizerDiv && (
                    <div aria-hidden style={{height: 0, overflow: 'hidden'}}>
                        {sizerDiv}
                    </div>
                )}
            </div>
        );
    }
);

OptionsList.displayName = 'OptionsList';
