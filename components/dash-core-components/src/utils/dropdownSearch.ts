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

    // Convert to lowercase for case insensitive comparison
    const searchLower = searchValue.toLowerCase();
    const labelMap = new Map(
        filtered.map(opt => [
            opt.value,
            String(opt.label ?? opt.value).toLowerCase(),
        ])
    );
    // Sort results by match relevance
    const sorted = filtered.sort((a, b) => {
        const aLabel = labelMap.get(a.value)!;
        const bLabel = labelMap.get(b.value)!;
        // Label starts with search value
        const aStartsWith = aLabel.startsWith(searchLower);
        const bStartsWith = bLabel.startsWith(searchLower);
        if (aStartsWith && !bStartsWith) {
            return -1;
        }
        if (!aStartsWith && bStartsWith) {
            return 1;
        }
        // Check for word boundary match (space followed by search term)
        const aWordStart = aLabel.includes(' ' + searchLower);
        const bWordStart = bLabel.includes(' ' + searchLower);
        if (aWordStart && !bWordStart) {
            return -1;
        }
        if (!aWordStart && bWordStart) {
            return 1;
        }
        // Everything else (substring match)
        return 0;
    });

    return {
        sanitizedOptions: sanitized || [],
        filteredOptions: sorted || [],
    };
}
