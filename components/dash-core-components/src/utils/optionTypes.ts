import React from 'react';
import {DetailedOption, DropdownProps, OptionValue} from '../types';

const isOptionValue = (option: unknown): option is OptionValue => {
    return ['string', 'number', 'boolean'].includes(typeof option);
};

export interface SanitizedResult {
    options: DetailedOption[];
    valueSet: Set<OptionValue>;
}

export const sanitizeOptions = (
    options: DropdownProps['options']
): SanitizedResult => {
    const valueSet = new Set<OptionValue>();
    let result: DetailedOption[];

    if (typeof options === 'object' && !(options instanceof Array)) {
        result = Object.entries(options).map(([value, label]) => {
            const opt = {
                label: React.isValidElement(label) ? label : String(label),
                value,
            };
            valueSet.add(value);
            return opt;
        });
    } else if (options instanceof Array) {
        result = options.map(option => {
            const opt = isOptionValue(option)
                ? {label: String(option), value: option}
                : option;
            valueSet.add(opt.value);
            return opt;
        });
    } else {
        result = [];
    }

    return {options: result, valueSet};
};
