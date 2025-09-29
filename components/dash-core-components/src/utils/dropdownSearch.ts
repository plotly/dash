import React from 'react';
import {
    Search,
    AllSubstringsIndexStrategy,
    UnorderedSearchIndex,
} from 'js-search';
import {sanitizeOptions} from './optionTypes';
import {DetailedOption, DropdownProps} from '../types';

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

interface FilteredOptionsResult {
    sanitizedOptions: DetailedOption[];
    filteredOptions: DetailedOption[];
}

/**
 * Creates filtered dropdown options using js-search with the exact same behavior
 * as react-select-fast-filter-options
 */
export function createFilteredOptions(
    options: DropdownProps['options'],
    searchable: boolean,
    searchValue?: string
): FilteredOptionsResult {
    // Sanitize and prepare options
    let sanitized = sanitizeOptions(options);

    const indexes = ['value'];
    let hasElement = false,
        hasSearch = false;

    sanitized = Array.isArray(sanitized)
        ? sanitized.map(option => {
              if (option.search) {
                  hasSearch = true;
              }
              if (React.isValidElement(option.label)) {
                  hasElement = true;
              }
              return option;
          })
        : sanitized;

    if (!hasElement) {
        indexes.push('label');
    }
    if (hasSearch) {
        indexes.push('search');
    }

    // If not searchable or no search value, return all sanitized options
    if (!searchable || !searchValue) {
        return {
            sanitizedOptions: sanitized || [],
            filteredOptions: sanitized || [],
        };
    }

    // Create js-search instance exactly like react-select-fast-filter-options
    const search = new Search('value'); // valueKey defaults to 'value'
    search.searchIndex = new UnorderedSearchIndex();
    search.indexStrategy = new AllSubstringsIndexStrategy();
    search.tokenizer = TOKENIZER;

    // Add indexes
    indexes.forEach(index => {
        search.addIndex(index);
    });

    // Add documents
    if (sanitized && sanitized.length > 0) {
        search.addDocuments(sanitized);
    }

    const filtered = search.search(searchValue) as DetailedOption[];

    return {
        sanitizedOptions: sanitized || [],
        filteredOptions: filtered || [],
    };
}
