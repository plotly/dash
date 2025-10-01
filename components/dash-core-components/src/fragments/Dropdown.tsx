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
import {DetailedOption, DropdownProps, OptionValue} from '../types';
import {OptionsList, OptionLabel} from '../utils/optionRendering';
import uuid from 'uniqid';

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
    const [optionsCheck, setOptionsCheck] = useState<DetailedOption[]>();
    const [isOpen, setIsOpen] = useState(false);
    const [displayOptions, setDisplayOptions] = useState<DetailedOption[]>([]);
    const persistentOptions = useRef<DropdownProps['options']>([]);
    const dropdownContainerRef = useRef<HTMLButtonElement>(null);

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

    const sanitizedValues: OptionValue[] = useMemo(() => {
        if (value instanceof Array) {
            return value;
        }
        if (isNil(value)) {
            return [];
        }
        return [value];
    }, [value]);

    const updateSelection = useCallback(
        (selection: OptionValue[]) => {
            if (closeOnSelect !== false) {
                setIsOpen(false);
            }

            if (multi) {
                // For multi-select, validate the selection respects clearable rules
                if (selection.length === 0) {
                    // Empty selection: only allow if clearable is true
                    if (clearable) {
                        setProps({value: []});
                    }
                    // If clearable is false and trying to set empty, do nothing
                    // return;
                } else {
                    // Non-empty selection: always allowed in multi-select
                    setProps({value: selection});
                }
            } else {
                // For single-select, take the first value or null
                if (selection.length === 0) {
                    // Empty selection: only allow if clearable is true
                    if (clearable) {
                        setProps({value: null});
                    }
                    // If clearable is false and trying to set empty, do nothing
                    // return;
                } else {
                    // Take the first value for single-select
                    setProps({value: selection[selection.length - 1]});
                }
            }
        },
        [multi, clearable, closeOnSelect]
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
                    {option && <OptionLabel {...option} index={i} />}
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
                const selectedOptions: DetailedOption[] = [];
                const unselectedOptions: DetailedOption[] = [];

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

    const accessibleId = id ?? uuid();

    return (
        <Popover.Root open={isOpen} onOpenChange={handleOpenChange}>
            <Popover.Trigger asChild>
                <button
                    id={id}
                    ref={dropdownContainerRef}
                    disabled={disabled}
                    type="button"
                    onKeyDown={e => {
                        if (e.key === 'ArrowDown') {
                            setIsOpen(true);
                        }
                    }}
                    className={`dash-dropdown ${className ?? ''}`}
                    style={style}
                    aria-labelledby={`${accessibleId}-value-count ${accessibleId}-value`}
                    aria-haspopup="listbox"
                    aria-expanded={isOpen}
                    data-dash-is-loading={loading || undefined}
                >
                    <span className="dash-dropdown-grid-container dash-dropdown-trigger">
                        {displayValue.length > 0 && (
                            <span
                                id={accessibleId + '-value'}
                                className="dash-dropdown-value"
                            >
                                {displayValue}
                            </span>
                        )}
                        {displayValue.length === 0 && (
                            <span
                                id={accessibleId + '-value'}
                                className="dash-dropdown-value dash-dropdown-placeholder"
                            >
                                {props.placeholder}
                            </span>
                        )}
                        {sanitizedValues.length > 1 && (
                            <span
                                id={accessibleId + '-value-count'}
                                className="dash-dropdown-value-count"
                            >
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
                    </span>
                </button>
            </Popover.Trigger>

            <Popover.Portal>
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
                                onChange={e => onInputChange(e.target.value)}
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
                    {isOpen && !!displayOptions.length && (
                        <>
                            <OptionsList
                                options={displayOptions}
                                selected={sanitizedValues}
                                onSelectionChange={updateSelection}
                                className="dash-dropdown-options"
                                optionClassName="dash-dropdown-option"
                                optionStyle={{
                                    height: optionHeight
                                        ? `${optionHeight}px`
                                        : undefined,
                                }}
                            />
                        </>
                    )}
                    {isOpen && search_value && !displayOptions.length && (
                        <div className="dash-dropdown-options">
                            <span className="dash-dropdown-option">
                                {localizations?.no_options_found}
                            </span>
                        </div>
                    )}
                </Popover.Content>
            </Popover.Portal>
        </Popover.Root>
    );
};

export default Dropdown;
