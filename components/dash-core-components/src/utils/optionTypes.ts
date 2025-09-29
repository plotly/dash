import React from 'react';
import {DetailedOption, DropdownProps, OptionValue} from '../types';

const isOptionValue = (option: unknown): option is OptionValue => {
    return ['string', 'number', 'boolean'].includes(typeof option);
};

export const sanitizeOptions = (
    options: DropdownProps['options']
): DetailedOption[] => {
    if (typeof options === 'object' && !(options instanceof Array)) {
        return Object.entries(options).map(([value, label]) => ({
            label: React.isValidElement(label) ? label : String(label),
            value,
        }));
    }

    if (options instanceof Array) {
        return options.map(option => {
            return isOptionValue(option)
                ? {label: String(option), value: option}
                : option;
        });
    }

    return [];
};
