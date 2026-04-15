import React, {lazy, Suspense} from 'react';
import {DropdownProps, PersistedProps, PersistenceTypes} from '../types';
import dropdown from '../utils/LazyLoader/dropdown';

const RealDropdown = lazy(dropdown);

const defaultLabels: DropdownProps['labels'] = {
    select_all: 'Select All',
    deselect_all: 'Deselect All',
    selected_count: '{num_selected} selected',
    search: 'Search',
    clear_search: 'Clear search',
    clear_selection: 'Clear selection',
    no_options_found: 'No options found',
};

/**
 * Dropdown is an interactive dropdown element for selecting one or more
 * items.
 * The values and labels of the dropdown items are specified in the `options`
 * property and the selected item(s) are specified with the `value` property.
 *
 * Use a dropdown when you have many options (more than 5) or when you are
 * constrained for space. Otherwise, you can use RadioItems or a Checklist,
 * which have the benefit of showing the users all of the items at once.
 */
export default function Dropdown({
    clearable = true,
    disabled = false,
    multi = false,
    searchable = true,
    labels = defaultLabels,
    optionHeight = 'auto',
    // eslint-disable-next-line no-magic-numbers
    maxHeight = 200,
    closeOnSelect = !multi,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persisted_props = [PersistedProps.value],
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persistence_type = PersistenceTypes.local,
    ...props
}: DropdownProps) {
    labels = {
        ...defaultLabels,
        ...labels,
    };

    return (
        <Suspense fallback={null}>
            <RealDropdown
                clearable={clearable}
                disabled={disabled}
                labels={labels}
                multi={multi}
                searchable={searchable}
                optionHeight={optionHeight}
                maxHeight={maxHeight}
                closeOnSelect={closeOnSelect}
                {...props}
            />
        </Suspense>
    );
}

Dropdown.dashPersistence = {
    persisted_props: [PersistedProps.value],
    persistence_type: PersistenceTypes.local,
};
