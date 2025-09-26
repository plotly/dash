import React from 'react';
import {append, includes, without} from 'ramda';
import {DetailedOption, OptionValue} from 'src/types';
import '../components/css/optionslist.css';

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

interface OptionProps extends StylingProps {
    index: number;
    option: DetailedOption;
    isSelected: boolean;
    onChange: (option: DetailedOption) => void;
}

export function OptionLabel(
    props: DetailedOption & {index: string | number}
): JSX.Element {
    const ctx = window.dash_component_api.useDashContext();
    const ExternalWrapper = window.dash_component_api.ExternalWrapper;

    if (typeof props.label === 'object') {
        const labels =
            props.label instanceof Array ? props.label : [props.label];
        return (
            <>
                {labels.map((label, i) => (
                    <ExternalWrapper
                        key={i}
                        component={label}
                        componentPath={[...ctx.componentPath, props.index, i]}
                    />
                ))}
            </>
        );
    }

    const displayLabel = `${props.label ?? props.value}`;
    return <span title={props.title}>{displayLabel}</span>;
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
        >
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
                readOnly
                className={inputClassNames.join(' ')}
                style={inputStyle}
            />
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

interface OptionsListProps extends StylingProps {
    options: DetailedOption[];
    selected: OptionValue[];
    onSelectionChange: (selected: OptionValue[]) => void;
}

export const OptionsList: React.FC<OptionsListProps> = ({
    options,
    selected,
    onSelectionChange,
    id,
    className,
    style,
    ...passThruProps
}) => {
    const classNames = ['dash-options-list', className].filter(Boolean);
    return (
        <div id={id} className={classNames.join(' ')} style={style}>
            {options.map((option, i) => {
                const isSelected = includes(option.value, selected);
                return (
                    <Option
                        id={id}
                        key={i}
                        index={i}
                        option={option}
                        isSelected={isSelected}
                        onChange={option => {
                            let newValue: OptionValue[];
                            if (includes(option.value, selected)) {
                                newValue = without([option.value], selected);
                            } else {
                                newValue = append(option.value, selected);
                            }
                            onSelectionChange(newValue);
                        }}
                        {...passThruProps}
                    />
                );
            })}
        </div>
    );
};
