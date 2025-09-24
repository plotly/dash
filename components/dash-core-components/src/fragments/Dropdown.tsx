import {isNil, without, isEmpty} from 'ramda';
import React, {
    useState,
    useCallback,
    useEffect,
    useMemo,
    useRef,
    MouseEvent,
} from 'react';
import {createFilteredOptions} from '../utils/dropdownSearch';
import {
    CaretDownIcon,
    MagnifyingGlassIcon,
    Cross1Icon,
} from '@radix-ui/react-icons';
import * as Popover from '@radix-ui/react-popover';
import '../components/css/dropdown.css';

import isEqual from 'react-fast-compare';
import {DetailedDropdownOption, DropdownProps, DropdownValue} from '../types';

interface DropdownOptionProps {
    index: number;
    option: DetailedDropdownOption;
    isSelected: boolean;
    onClick: (option: DetailedDropdownOption) => void;
    style?: React.CSSProperties;
}

function DropdownLabel(
    props: DetailedDropdownOption & {index: string | number}
): JSX.Element {
    const ctx = window.dash_component_api.useDashContext();
    const ExternalWrapper = window.dash_component_api.ExternalWrapper;

    if (typeof props.label === 'object') {
        return (
            <ExternalWrapper
                component={props.label}
                componentPath={[...ctx.componentPath, props.index]}
            />
        );
    }
    const displayLabel = `${props.label ?? props.value}`;
    return <span title={props.title}>{displayLabel}</span>;
}

const DropdownOption: React.FC<DropdownOptionProps> = ({
    option,
    isSelected,
    onClick,
    style,
    index,
}) => {
    return (
        <label
            className={`dash-dropdown-option ${isSelected ? 'selected' : ''}`}
            role="option"
            aria-selected={isSelected}
            style={style}
            title={option.title}
        >
            <input
                type="checkbox"
                checked={isSelected}
                value={
                    typeof option.value === 'boolean'
                        ? `${option.value}`
                        : option.value
                }
                disabled={!!option.disabled}
                onChange={() => onClick(option)}
                readOnly
                className="dash-dropdown-option-checkbox"
            />
            <span className="dash-dropdown-option-text">
                <DropdownLabel {...option} index={index} />
            </span>
        </label>
    );
};

const Dropdown = (props: DropdownProps) => {
    const {
        id,
        className,
        closeOnSelect,
        clearable,
        disabled,
        localizations,
        maxHeight,
        multi,
        options,
        optionHeight,
        setProps,
        searchable,
        search_value,
        style,
        value,
    } = props;
    const [optionsCheck, setOptionsCheck] =
        useState<DetailedDropdownOption[]>();
    const [isOpen, setIsOpen] = useState(false);
    const [displayOptions, setDisplayOptions] = useState<
        DetailedDropdownOption[]
    >([]);
    const persistentOptions = useRef<DropdownProps['options']>([]);
    const dropdownContainerRef = useRef<HTMLDivElement>(null);

    const ctx = window.dash_component_api.useDashContext();
    const loading = ctx.useLoading();

    if (!persistentOptions || !isEqual(options, persistentOptions.current)) {
        persistentOptions.current = options;
    }

    const {sanitizedOptions, filteredOptions} = useMemo(
        () =>
            createFilteredOptions(
                persistentOptions.current,
                !!searchable,
                search_value
            ),
        [persistentOptions.current, searchable, search_value]
    );

    const sanitizedValues: DropdownValue[] = useMemo(() => {
        if (value instanceof Array) {
            return value;
        }
        if (isNil(value)) {
            return [];
        }
        return [value];
    }, [value]);

    const toggleOption = useCallback(
        (option: DetailedDropdownOption) => {
            const isCurrentlySelected = sanitizedValues.includes(option.value);

            // Close dropdown if closeOnSelect is true (default behavior)
            if (closeOnSelect !== false) {
                setIsOpen(false);
            }

            if (multi) {
                let newValues: DropdownValue[];

                if (isCurrentlySelected) {
                    // Deselecting: only allow if clearable is true or more than one option selected
                    if (clearable || sanitizedValues.length > 1) {
                        newValues = sanitizedValues.filter(
                            v => v !== option.value
                        );
                    } else {
                        // Cannot deselect the last option when clearable is false
                        return;
                    }
                } else {
                    // Selecting: add to current selection
                    newValues = [...sanitizedValues, option.value];
                }

                setProps({value: newValues});
            } else {
                let newValue: DropdownValue | null;

                if (isCurrentlySelected) {
                    // Deselecting: only allow if clearable is true
                    if (clearable) {
                        newValue = null;
                    } else {
                        // Cannot deselect when clearable is false
                        return;
                    }
                } else {
                    // Selecting: set as the single value
                    newValue = option.value;
                }

                setProps({value: newValue});
            }
        },
        [multi, clearable, closeOnSelect, sanitizedValues]
    );

    const onInputChange = useCallback(
        search_value => setProps({search_value}),
        []
    );

    const handleClearSearch = useCallback((e: MouseEvent) => {
        if (e.currentTarget instanceof HTMLElement) {
            const parentElement = e.currentTarget.parentElement;
            parentElement?.querySelector('input')?.focus();
        }
        setProps({search_value: undefined});
    }, []);

    useEffect(() => {
        if (
            !search_value &&
            !isNil(sanitizedOptions) &&
            optionsCheck !== sanitizedOptions &&
            !isNil(value) &&
            !isEmpty(value)
        ) {
            const values = sanitizedOptions.map(option => option.value);
            if (Array.isArray(value)) {
                if (multi) {
                    const invalids = value.filter(v => !values.includes(v));
                    if (invalids.length) {
                        setProps({value: without(invalids, value)});
                    }
                }
            } else {
                if (!values.includes(value)) {
                    setProps({value: null});
                }
            }
            setOptionsCheck(sanitizedOptions);
        }
    }, [sanitizedOptions, optionsCheck, multi, value]);

    const displayValue = useMemo(() => {
        const labels = sanitizedValues.map((val, i) => {
            const option = sanitizedOptions.find(
                option => option.value === val
            );
            return (
                <React.Fragment key={`${option?.value}-${i}`}>
                    {option && <DropdownLabel {...option} index={i} />}
                    {i === sanitizedValues.length - 1 ? '' : ', '}
                </React.Fragment>
            );
        });
        return labels;
    }, [sanitizedOptions, sanitizedValues]);

    const canDeselectAll = useMemo(() => {
        if (clearable) {
            return true;
        }
        return !sanitizedValues.every(value =>
            displayOptions.some(option => option.value === value)
        );
    }, [clearable, sanitizedValues, displayOptions, search_value]);

    const handleOptionClick = useCallback(
        (option: DetailedDropdownOption) => {
            toggleOption(option);
        },
        [toggleOption]
    );

    const handleClear = useCallback(() => {
        const finalValue: DropdownProps['value'] = multi ? [] : null;
        setProps({value: finalValue});
    }, [multi]);

    const handleSelectAll = useCallback(() => {
        if (multi) {
            const allValues = sanitizedValues.concat(
                displayOptions
                    .filter(option => !sanitizedValues.includes(option.value))
                    .map(option => option.value)
            );
            setProps({value: allValues});
        }
        if (closeOnSelect) {
            setIsOpen(false);
        }
    }, [multi, displayOptions, sanitizedValues, closeOnSelect]);

    const handleDeselectAll = useCallback(() => {
        if (multi) {
            const withDeselected = sanitizedValues.filter(option => {
                return !displayOptions.some(
                    displayOption => displayOption.value === option
                );
            });
            setProps({value: withDeselected});
        }
        if (closeOnSelect) {
            setIsOpen(false);
        }
    }, [multi, displayOptions, sanitizedValues, closeOnSelect]);

    // Sort options when popover opens - selected options first
    // Update display options when filtered options or selection changes
    useEffect(() => {
        if (isOpen) {
            // Sort filtered options: selected first, then unselected
            const sortedOptions = [...filteredOptions].sort((a, b) => {
                const aSelected = sanitizedValues.includes(a.value);
                const bSelected = sanitizedValues.includes(b.value);

                if (aSelected && !bSelected) {
                    return -1;
                }
                if (!aSelected && bSelected) {
                    return 1;
                }
                return 0; // Maintain original order within each group
            });

            setDisplayOptions(sortedOptions);
        }
    }, [filteredOptions, isOpen]); // Removed sanitizedValues to prevent re-sorting on selection changes

    // Handle keyboard navigation in popover
    const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
        const relevantKeys = [
            'ArrowDown',
            'ArrowUp',
            'PageDown',
            'PageUp',
            'Home',
            'End',
        ];
        if (!relevantKeys.includes(e.key)) {
            return;
        }

        // Don't interfere with the event if the user is using Home/End keys on the search input
        if (
            ['Home', 'End'].includes(e.key) &&
            document.activeElement instanceof HTMLInputElement
        ) {
            return;
        }

        const focusableElements = e.currentTarget.querySelectorAll(
            'input[type="search"], input[type="checkbox"]:not([disabled])'
        ) as NodeListOf<HTMLElement>;

        // Don't interfere with the event if there aren't any options that the user can interact with
        if (focusableElements.length === 0) {
            return;
        }

        e.preventDefault();

        const currentIndex = Array.from(focusableElements).indexOf(
            document.activeElement as HTMLElement
        );
        let nextIndex = -1;

        switch (e.key) {
            case 'ArrowDown':
                nextIndex =
                    currentIndex < focusableElements.length - 1
                        ? currentIndex + 1
                        : 0;
                break;

            case 'ArrowUp':
                nextIndex =
                    currentIndex > 0
                        ? currentIndex - 1
                        : focusableElements.length - 1;

                break;
            case 'PageDown':
                nextIndex = Math.min(
                    currentIndex + 10,
                    focusableElements.length - 1
                );
                break;
            case 'PageUp':
                nextIndex = Math.max(currentIndex - 10, 0);
                break;
            case 'Home':
                nextIndex = 0;
                break;
            case 'End':
                nextIndex = focusableElements.length - 1;
                break;
            default:
                break;
        }

        if (nextIndex > -1) {
            focusableElements[nextIndex].focus();
            focusableElements[nextIndex].scrollIntoView({
                behavior: 'auto',
                block: 'center',
            });
        }
    }, []);

    // Handle popover open/close
    const handleOpenChange = useCallback(
        (open: boolean) => {
            setIsOpen(open);

            if (open) {
                // Sort options: selected first, then unselected
                const selectedOptions: DetailedDropdownOption[] = [];
                const unselectedOptions: DetailedDropdownOption[] = [];

                // First, collect selected options in the order they appear in the `value` array
                sanitizedValues.forEach(value => {
                    const option = filteredOptions.find(
                        opt => opt.value === value
                    );
                    if (option) {
                        selectedOptions.push(option);
                    }
                });

                // Then, collect unselected options in the order they appear in `options` array
                filteredOptions.forEach(option => {
                    if (!sanitizedValues.includes(option.value)) {
                        unselectedOptions.push(option);
                    }
                });
                const sortedOptions = [
                    ...selectedOptions,
                    ...unselectedOptions,
                ];
                setDisplayOptions(sortedOptions);
            } else {
                setProps({search_value: undefined});
            }
        },
        [filteredOptions, sanitizedValues]
    );

    return (
        <div
            id={id}
            ref={dropdownContainerRef}
            className={`dash-dropdown ${className ?? ''}`}
            style={style}
            data-dash-is-loading={loading || undefined}
        >
            <Popover.Root open={isOpen} onOpenChange={handleOpenChange}>
                <Popover.Trigger asChild>
                    <button
                        className="dash-dropdown-grid-container dash-dropdown-trigger"
                        aria-label={props.placeholder}
                        disabled={disabled}
                        type="button"
                        onKeyDown={e => {
                            if (e.key === 'ArrowDown') {
                                setIsOpen(true);
                            }
                        }}
                    >
                        {displayValue.length > 0 && (
                            <span className="dash-dropdown-value">
                                {displayValue}
                            </span>
                        )}
                        {displayValue.length === 0 && (
                            <span className="dash-dropdown-value dash-dropdown-placeholder">
                                {props.placeholder}
                            </span>
                        )}
                        {sanitizedValues.length > 1 && (
                            <span className="dash-dropdown-value-count">
                                {localizations?.selected_count?.replace(
                                    '{num_selected}',
                                    `${sanitizedValues.length}`
                                )}
                            </span>
                        )}
                        {clearable && !disabled && !!sanitizedValues.length && (
                            <a
                                className="dash-dropdown-clear"
                                onClick={e => {
                                    e.preventDefault();
                                    handleClear();
                                }}
                                title={localizations?.clear_selection}
                                aria-label={localizations?.clear_selection}
                            >
                                <Cross1Icon />
                            </a>
                        )}

                        <CaretDownIcon className="dash-dropdown-trigger-icon" />
                    </button>
                </Popover.Trigger>

                <Popover.Portal container={dropdownContainerRef.current}>
                    <Popover.Content
                        className="dash-dropdown-content"
                        align="start"
                        sideOffset={5}
                        onOpenAutoFocus={e => e.preventDefault()}
                        onKeyDown={handleKeyDown}
                        style={{
                            maxHeight: maxHeight ? `${maxHeight}px` : 'auto',
                        }}
                    >
                        {searchable && (
                            <div className="dash-dropdown-grid-container dash-dropdown-search-container">
                                <MagnifyingGlassIcon className="dash-dropdown-search-icon" />
                                <input
                                    type="search"
                                    className="dash-dropdown-search"
                                    placeholder={localizations?.search}
                                    value={search_value || ''}
                                    autoComplete="off"
                                    onChange={e =>
                                        onInputChange(e.target.value)
                                    }
                                    autoFocus
                                />
                                {search_value && (
                                    <button
                                        type="button"
                                        className="dash-dropdown-clear"
                                        onClick={handleClearSearch}
                                        aria-label={localizations?.clear_search}
                                    >
                                        <Cross1Icon />
                                    </button>
                                )}
                            </div>
                        )}
                        {multi && (
                            <div className="dash-dropdown-actions">
                                <button
                                    type="button"
                                    className="dash-dropdown-action-button"
                                    onClick={handleSelectAll}
                                >
                                    {localizations?.select_all}
                                </button>
                                {canDeselectAll && (
                                    <button
                                        type="button"
                                        className="dash-dropdown-action-button"
                                        onClick={handleDeselectAll}
                                    >
                                        {localizations?.deselect_all}
                                    </button>
                                )}
                            </div>
                        )}
                        {isOpen && (
                            <div className="dash-dropdown-options">
                                {displayOptions.map((option, i) => {
                                    const isSelected = multi
                                        ? sanitizedValues.includes(option.value)
                                        : value === option.value;

                                    return (
                                        <DropdownOption
                                            key={`${option.value}-${i}`}
                                            index={i}
                                            option={option}
                                            isSelected={isSelected}
                                            onClick={handleOptionClick}
                                            style={{
                                                height: optionHeight
                                                    ? `${optionHeight}px`
                                                    : undefined,
                                            }}
                                        />
                                    );
                                })}
                                {search_value &&
                                    displayOptions.length === 0 && (
                                        <span className="dash-dropdown-option">
                                            {localizations?.no_options_found}
                                        </span>
                                    )}
                            </div>
                        )}
                    </Popover.Content>
                </Popover.Portal>
            </Popover.Root>
        </div>
    );
};

export default Dropdown;
