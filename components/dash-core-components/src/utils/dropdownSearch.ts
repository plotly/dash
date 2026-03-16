import React from 'react';
import {
    Search,
    AllSubstringsIndexStrategy,
    UnorderedSearchIndex,
} from 'js-search';
import {sanitizeOptions} from './optionTypes';
import {DetailedOption, DropdownProps, OptionValue} from '../types';

// Custom tokenizer, see https://github.com/bvaughn/js-search/issues/43
// Split on spaces
const REGEX = /\s+/;
const TOKENIZER = {
    tokenize(text: string) {
        return text.split(REGEX).filter(
            // Filter empty tokens
            text => text
        );
    },
};

export interface SanitizedOptions {
    options: DetailedOption[];
    indexes: string[];
    valueSet: Set<OptionValue>;
}

// Single-pass sanitization via sanitizeOptions, plus detection of
// search/element labels for indexing.
export function sanitizeDropdownOptions(
    options: DropdownProps['options']
): SanitizedOptions {
    const {options: sanitized, valueSet} = sanitizeOptions(options);

    const indexes = ['value'];
    let hasElement = false,
        hasSearch = false;

    for (const option of sanitized) {
        if (option.search) {
            hasSearch = true;
        }
        if (React.isValidElement(option.label)) {
            hasElement = true;
        }
        if (hasSearch && hasElement) {
            break;
        }
    }

    if (!hasElement) {
        indexes.push('label');
    }
    if (hasSearch) {
        indexes.push('search');
    }

    return {options: sanitized, indexes, valueSet};
}

export function filterOptions(
    options: SanitizedOptions,
    searchValue?: string
): DetailedOption[] {
    if (!searchValue) {
        return options.options;
    }

    const search = new Search('value');
    search.searchIndex = new UnorderedSearchIndex();
    search.indexStrategy = new AllSubstringsIndexStrategy();
    search.tokenizer = TOKENIZER;

    options.indexes.forEach(index => {
        search.addIndex(index);
    });

    if (options.options.length > 0) {
        search.addDocuments(options.options);
    }

    return (search.search(searchValue) as DetailedOption[]) || [];
}
