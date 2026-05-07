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
    search: Search;
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

    // Build the search index ONCE during sanitization
    const search = new Search('value');
    search.searchIndex = new UnorderedSearchIndex();
    search.indexStrategy = new AllSubstringsIndexStrategy();
    search.tokenizer = TOKENIZER;

    indexes.forEach(index => {
        search.addIndex(index);
    });

    if (sanitized.length > 0) {
        search.addDocuments(sanitized);
    }

    return {
        options: sanitized,
        indexes,
        valueSet,
        search,
    };
}

export function filterOptions(
    options: SanitizedOptions,
    searchValue?: string,
    searchOrder?: string
): DetailedOption[] {
    if (!searchValue) {
        return options.options;
    }

    const results =
        (options.search.search(searchValue) as DetailedOption[]) || [];

    // Preserve original option order
    if (searchOrder === 'original') {
        const resultSet = new Set(results.map(option => option.value));

        return options.options.filter(option =>
            resultSet.has(option.value)
        );
    }

    return results;
}
