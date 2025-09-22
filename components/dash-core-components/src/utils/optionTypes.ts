import React from 'react';
import {DetailedDropdownOption, DropdownProps, DropdownValue} from '../types';

const isDropdownValue = (option: unknown): option is DropdownValue => {
    return ['string', 'number', 'boolean'].includes(typeof option);
};

export const sanitizeOptions = (
    options: DropdownProps['options']
): DetailedDropdownOption[] => {
    if (typeof options === 'object' && !(options instanceof Array)) {
        return Object.entries(options).map(([value, label]) => ({
            label: React.isValidElement(label) ? label : String(label),
            value,
        }));
    }

    if (options instanceof Array) {
        return options.map(option => {
            return isDropdownValue(option)
                ? {label: String(option), value: option}
                : option;
        });
    }

    return options;
};
