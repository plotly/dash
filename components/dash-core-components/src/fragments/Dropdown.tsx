import {isNil, without, append, isEmpty} from 'ramda';
import React, {
    useState,
    useCallback,
    useEffect,
    useMemo,
    useRef,
    MouseEvent,
} from 'react';
import {sanitizeDropdownOptions, filterOptions} from '../utils/dropdownSearch';
import {
    CaretDownIcon,
    MagnifyingGlassIcon,
    Cross1Icon,
} from '@radix-ui/react-icons';
import * as Popover from '@radix-ui/react-popover';
import '../components/css/dropdown.css';

import isEqual from 'react-fast-compare';
import {DetailedOption, DropdownProps, OptionValue} from '../types';
import {
    OptionsList,
    OptionsListHandle,
    OptionLabel,
} from '../utils/optionRendering';
import uuid from 'uniqid';

const Dropdown = (props: DropdownProps) => {
    const {
        id,
        className,
        closeOnSelect,
        clearable,
        debounce,
        disabled,
        labels,
        maxHeight,
        multi,
        options,
        optionHeight,
        setProps,
        searchable,
        search_value,
        search_order,
        style,
        value,
    } = props;
    const [optionsCheck, setOptionsCheck] = useState<DetailedOption[]>();
    const [isOpen, setIsOpen] = useState(false);
    const [displayOptions, setDisplayOptions] = useState<DetailedOption[]>([]);
    const [val, setVal] = useState<DropdownProps['value']>(value);
    const persistentOptions = useRef<DropdownProps['options']>([]);
    const dropdownContainerRef = useRef<HTMLButtonElement>(null);
    const dropdownContentRef = useRef<HTMLDivElement>(
        document.createElement('div')
    );
    const searchInputRef = useRef<HTMLInputElement>(null);
    const optionsListRef = useRef<OptionsListHandle>(null);
    const focusedIndexRef = useRef(-1);
    const pendingSearchRef = useRef('');

    const ctx = window.dash_component_api.useDashContext();
    const loading = ctx.useLoading();

    // Sync val when external value prop changes
    useEffect(() => {
        if (!isEqual(value, val)) {
            setVal(value);
        }
    }, [value]);

    if (!persistentOptions || !isEqual(options, persistentOptions.current)) {
        persistentOptions.current = options;
    }

    const sanitized = useMemo(
        () => sanitizeDropdownOptions(persistentOptions.current),
        [persistentOptions.current]
    );
    const sanitizedOptions = sanitized.options;

    const filteredOptions = useMemo(
        () =>
            searchable
                ? filterOptions(sanitized, search_value, search_order)
                : sanitizedOptions,
        [sanitized, searchable, search_value, search_order]
    );

    const sanitizedValues: OptionValue[] = useMemo(() => {
        if (val instanceof Array) {
            return val;
        }
        if (isNil(val)) {
            return [];
        }
        return [val];
    }, [val]);

    const handleSetProps = useCallback(
        (newValue: DropdownProps['value']) => {
            if (debounce && isOpen) {
                // local only
                setVal(newValue);
            } else {
                setVal(newValue);
                setProps({value: newValue});
            }
        },
        [debounce, isOpen, setProps]
    );

    const updateSelection = useCallback(
        (selection: OptionValue[]) => {
            if (closeOnSelect !== false) {
                setIsOpen(false);
                setProps({search_value: undefined});
                pendingSearchRef.current = '';
            }

            if (multi) {
                // For multi-select, validate the selection respects clearable rules
                if (selection.length === 0) {
                    // Empty selection: only allow if clearable is true
                    if (clearable) {
                        handleSetProps([]);
                    }
                    // If clearable is false and trying to set empty, do nothing
                    // return;
                } else {
                    handleSetProps(selection);
                }
            } else {
                // For single-select, take the first value or null
                if (selection.length === 0) {
                    // Empty selection: only allow if clearable is true
                    if (clearable) {
                        handleSetProps(null);
                    }
                    // If clearable is false and trying to set empty, do nothing
                    // return;
                } else {
                    handleSetProps(selection[selection.length - 1]);
                }
            }
        },
        [multi, clearable, closeOnSelect, handleSetProps]
    );

    const onInputChange = useCallback(
        (search_value: string) => setProps({search_value}),
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
            const {valueSet} = sanitized;
            if (Array.isArray(value)) {
                if (multi) {
                    const invalids = value.filter(v => !valueSet.has(v));
                    if (invalids.length) {
                        setProps({value: without(invalids, value)});
                    }
                }
            } else {
                if (!valueSet.has(value)) {
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
                <span
                    key={`${option?.value}-${i}`}
                    className="dash-dropdown-value-item"
                >
                    {option && <OptionLabel {...option} index={i} />}
                </span>
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
        handleSetProps(finalValue);
    }, [multi, handleSetProps]);

    const handleSelectAll = useCallback(() => {
        if (multi) {
            const allValues = sanitizedValues.concat(
                displayOptions
                    .filter(option => !sanitizedValues.includes(option.value))
                    .map(option => option.value)
            );
            handleSetProps(allValues);
        }
        if (closeOnSelect) {
            setIsOpen(false);
        }
    }, [multi, displayOptions, sanitizedValues, closeOnSelect, handleSetProps]);

    const handleDeselectAll = useCallback(() => {
        if (multi) {
            const withDeselected = sanitizedValues.filter(option => {
                return !displayOptions.some(
                    displayOption => displayOption.value === option
                );
            });
            handleSetProps(withDeselected);
        }
        if (closeOnSelect) {
            setIsOpen(false);
        }
    }, [multi, displayOptions, sanitizedValues, closeOnSelect, handleSetProps]);

    // Sort options when popover opens - selected options first
    // Update display options when filtered options or selection changes
    useEffect(() => {
        if (isOpen) {
            let sortedOptions = filteredOptions;
            if (multi) {
                // Sort filtered options: selected first, then unselected
                sortedOptions = [...filteredOptions].sort((a, b) => {
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
            }

            setDisplayOptions(sortedOptions);
        }
    }, [filteredOptions, isOpen]);

    // Focus first selected item or search input when dropdown opens.
    // Depends on displayOptions so it fires after OptionsList is mounted.
    useEffect(() => {
        if (!isOpen || pendingSearchRef.current || !displayOptions.length) {
            return;
        }

        // Don't steal focus from the search input during search-driven
        // re-renders (displayOptions changes while the user is typing).
        if (document.activeElement === searchInputRef.current) {
            return;
        }

        requestAnimationFrame(() => {
            if (!multi) {
                const selectedValue = sanitizedValues[0];
                if (selectedValue) {
                    const selectedIndex = displayOptions.findIndex(
                        o => o.value === selectedValue
                    );
                    if (selectedIndex >= 0) {
                        focusedIndexRef.current = selectedIndex;
                        optionsListRef.current?.focusItem(selectedIndex);
                        return;
                    }
                }
            }

            if (searchable) {
                searchInputRef.current?.focus();
            } else {
                focusedIndexRef.current = 0;
                optionsListRef.current?.focusItem(0);
            }
        });
    }, [isOpen, multi, displayOptions]);

    // Handle keyboard navigation in popover.
    // Index -1 = search input, 0..N-1 = option index in displayOptions.
    const handleKeyDown = useCallback(
        (e: React.KeyboardEvent) => {
            const relevantKeys = [
                'ArrowDown',
                'ArrowUp',
                'Tab',
                'PageDown',
                'PageUp',
                'Home',
                'End',
            ];
            if (!relevantKeys.includes(e.key)) {
                return;
            }

            if (
                ['Home', 'End'].includes(e.key) &&
                document.activeElement === searchInputRef.current
            ) {
                return;
            }

            if (displayOptions.length === 0) {
                return;
            }

            e.preventDefault();

            const hasSearch = !!searchable;
            const current = focusedIndexRef.current;
            const maxIndex = displayOptions.length - 1;
            const minIndex = hasSearch ? -1 : 0;
            let nextIndex: number;

            switch (e.key) {
                case 'Tab': {
                    // Trap Tab inside the popover so Safari (which
                    // skips non-text inputs) can navigate options.
                    const next = current + (e.shiftKey ? -1 : 1);
                    if (next < minIndex) {
                        nextIndex = maxIndex;
                    } else if (next > maxIndex) {
                        nextIndex = minIndex;
                    } else {
                        nextIndex = next;
                    }
                    break;
                }
                case 'ArrowDown':
                    nextIndex = current < maxIndex ? current + 1 : minIndex;
                    break;
                case 'ArrowUp':
                    nextIndex = current > minIndex ? current - 1 : maxIndex;
                    break;
                case 'PageDown':
                    nextIndex = Math.min(current + 10, maxIndex);
                    break;
                case 'PageUp':
                    nextIndex = Math.max(current - 10, minIndex);
                    break;
                case 'Home':
                    nextIndex = minIndex;
                    break;
                case 'End':
                    nextIndex = maxIndex;
                    break;
                default:
                    return;
            }

            focusedIndexRef.current = nextIndex;

            if (nextIndex === -1) {
                searchInputRef.current?.focus();
                dropdownContentRef.current?.scrollTo({top: 0});
            } else {
                optionsListRef.current?.focusItem(nextIndex);
            }
        },
        [displayOptions.length, searchable]
    );

    const handleOpenChange = useCallback(
        (open: boolean) => {
            setIsOpen(open);
            focusedIndexRef.current = -1;

            if (!open) {
                pendingSearchRef.current = '';
                const updates: Partial<DropdownProps> = {};

                if (!isNil(search_value)) {
                    updates.search_value = undefined;
                }

                // Commit debounced value on close only
                if (debounce && !isEqual(value, val)) {
                    updates.value = val;
                }

                if (Object.keys(updates).length > 0) {
                    setProps(updates);
                }
            }
        },
        [debounce, value, val, search_value, setProps]
    );

    const accessibleId = id ?? uuid();
    const positioningContainerRef = useRef<HTMLDivElement>(null);
    const canClearValues = clearable && !disabled && !!sanitizedValues.length;

    const popover = (
        <Popover.Root open={isOpen} onOpenChange={handleOpenChange}>
            {/* Safari skips <button> in the Tab order; this hidden
                input receives Tab focus and delegates to the button. */}
            <input
                className="dash-dropdown-focus-target"
                tabIndex={disabled ? -1 : 0}
                readOnly
                aria-hidden="true"
                onFocus={e => {
                    if (e.relatedTarget !== dropdownContainerRef.current) {
                        e.currentTarget.tabIndex = -1;
                        dropdownContainerRef.current?.focus();
                    }
                }}
                onClick={() => {
                    dropdownContainerRef.current?.click();
                }}
            />
            <Popover.Trigger asChild>
                <button
                    id={id}
                    ref={dropdownContainerRef}
                    disabled={disabled}
                    type="button"
                    tabIndex={-1}
                    onBlur={e => {
                        const dummyInput =
                            e.currentTarget.previousElementSibling;
                        if (dummyInput instanceof HTMLElement) {
                            dummyInput.tabIndex = 0;
                        }
                    }}
                    onKeyDown={e => {
                        if (['ArrowDown', 'Enter'].includes(e.key)) {
                            e.preventDefault();
                        }
                    }}
                    onKeyUp={e => {
                        if (['ArrowDown', 'Enter'].includes(e.key)) {
                            setIsOpen(true);
                        }
                        if (
                            ['Delete', 'Backspace'].includes(e.key) &&
                            canClearValues
                        ) {
                            handleClear();
                        }
                        if (e.key.length === 1 && searchable) {
                            pendingSearchRef.current += e.key;
                            setProps({search_value: pendingSearchRef.current});
                            setIsOpen(true);
                            requestAnimationFrame(() =>
                                searchInputRef.current?.focus()
                            );
                        }
                    }}
                    className={`dash-dropdown ${className ?? ''}`}
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
                                {labels?.selected_count?.replace(
                                    '{num_selected}',
                                    `${sanitizedValues.length}`
                                )}
                            </span>
                        )}
                        {canClearValues && (
                            <a
                                className="dash-dropdown-clear"
                                onClick={e => {
                                    e.preventDefault();
                                    handleClear();
                                }}
                                title={labels?.clear_selection}
                                aria-label={labels?.clear_selection}
                            >
                                <Cross1Icon />
                            </a>
                        )}

                        <CaretDownIcon className="dash-dropdown-trigger-icon" />
                    </span>
                </button>
            </Popover.Trigger>

            <Popover.Portal
                // container is required otherwise popover will be rendered
                // at document root, which may be outside of the Dash app (i.e.
                // an embedded app)
                container={positioningContainerRef.current}
            >
                <Popover.Content
                    ref={dropdownContentRef}
                    className="dash-dropdown-content"
                    align="start"
                    sideOffset={5}
                    onOpenAutoFocus={e => e.preventDefault()}
                    onKeyDown={handleKeyDown}
                    style={{
                        maxHeight: maxHeight
                            ? `min(${maxHeight}px, calc(100vh - 100px))`
                            : 'calc(100vh - 100px)',
                    }}
                >
                    {searchable && (
                        <div className="dash-dropdown-grid-container dash-dropdown-search-container">
                            <MagnifyingGlassIcon className="dash-dropdown-search-icon" />
                            <input
                                type="search"
                                className="dash-dropdown-search"
                                placeholder={labels?.search}
                                value={search_value || ''}
                                autoComplete="off"
                                onChange={e => onInputChange(e.target.value)}
                                onKeyUp={e => {
                                    if (
                                        !search_value ||
                                        e.key !== 'Enter' ||
                                        !displayOptions.length
                                    ) {
                                        return;
                                    }
                                    const firstVal = displayOptions[0].value;
                                    const isSelected =
                                        sanitizedValues.includes(firstVal);
                                    let newSelection;
                                    if (isSelected) {
                                        newSelection = without(
                                            [firstVal],
                                            sanitizedValues
                                        );
                                    } else {
                                        newSelection = append(
                                            firstVal,
                                            sanitizedValues
                                        );
                                    }
                                    updateSelection(newSelection);
                                }}
                                ref={searchInputRef}
                            />
                            {search_value && (
                                <button
                                    type="button"
                                    className="dash-dropdown-clear"
                                    onClick={handleClearSearch}
                                    aria-label={labels?.clear_search}
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
                                {labels?.select_all}
                            </button>
                            {canDeselectAll && (
                                <button
                                    type="button"
                                    className="dash-dropdown-action-button"
                                    onClick={handleDeselectAll}
                                >
                                    {labels?.deselect_all}
                                </button>
                            )}
                        </div>
                    )}
                    {isOpen && !!displayOptions.length && (
                        <>
                            <OptionsList
                                ref={optionsListRef}
                                options={displayOptions}
                                selected={sanitizedValues}
                                onSelectionChange={updateSelection}
                                inputType={multi ? 'checkbox' : 'radio'}
                                className="dash-dropdown-options"
                                optionClassName="dash-dropdown-option"
                                optionHeight={
                                    typeof optionHeight === 'number'
                                        ? optionHeight
                                        : undefined
                                }
                                maxHeight={maxHeight}
                            />
                        </>
                    )}
                    {isOpen && search_value && !displayOptions.length && (
                        <div className="dash-dropdown-options">
                            <span className="dash-dropdown-option">
                                {labels?.no_options_found}
                            </span>
                        </div>
                    )}
                </Popover.Content>
            </Popover.Portal>
        </Popover.Root>
    );

    return (
        <div
            ref={positioningContainerRef}
            className="dash-dropdown-wrapper"
            style={style}
        >
            {popover}
        </div>
    );
};

export default Dropdown;
