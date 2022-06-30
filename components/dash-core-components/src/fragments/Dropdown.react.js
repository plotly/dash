import {isNil, pluck, without, pick, head} from 'ramda';
import React, {useState, useCallback, useEffect, useMemo} from 'react';
import ReactDropdown from 'react-virtualized-select';
import createFilterOptions from 'react-select-fast-filter-options';
import '../components/css/react-virtualized-select@3.1.0.css';
import '../components/css/react-virtualized@9.9.0.css';
import '../components/css/Dropdown.css';

import {propTypes, defaultProps} from '../components/Dropdown.react';
import {sanitizeOptions} from '../utils/optionTypes';

// Custom tokenizer, see https://github.com/bvaughn/js-search/issues/43
// Split on spaces
const REGEX = /\s+/;
const TOKENIZER = {
    tokenize(text) {
        return text.split(REGEX).filter(
            // Filter empty tokens
            text => text
        );
    },
};

const RDProps = [
    'multi',
    'clearable',
    'searchable',
    'search_value',
    'placeholder',
    'disabled',
    'optionHeight',
    'style',
    'className',
];

const Dropdown = props => {
    const {
        id,
        clearable,
        searchable,
        multi,
        options,
        setProps,
        style,
        loading_state,
        value,
    } = props;
    const [optionsCheck, setOptionsCheck] = useState(null);
    const [sanitizedOptions, filterOptions] = useMemo(() => {
        let sanitized = sanitizeOptions(options);
        const firstOption = sanitized ? head(sanitized) : null;
        let labelKey = 'label';
        if (firstOption && firstOption.search) {
            labelKey = 'search';
        } else if (firstOption && React.isValidElement(firstOption.label)) {
            // Auto put the value as search
            labelKey = 'search';
            sanitized = sanitized.map(option => ({
                ...option,
                search: `${option.value}`,
            }));
        }

        return [
            sanitized,
            createFilterOptions({
                options: sanitized,
                tokenizer: TOKENIZER,
                labelKey,
            }),
        ];
    }, [options]);

    const onChange = useCallback(
        selectedOption => {
            if (multi) {
                let value;
                if (isNil(selectedOption)) {
                    value = [];
                } else {
                    value = pluck('value', selectedOption);
                }
                setProps({value});
            } else {
                let value;
                if (isNil(selectedOption)) {
                    value = null;
                } else {
                    value = selectedOption.value;
                }
                setProps({value});
            }
        },
        [multi]
    );

    const onInputChange = useCallback(
        search_value => setProps({search_value}),
        []
    );

    useEffect(() => {
        if (
            !searchable &&
            !isNil(sanitizedOptions) &&
            optionsCheck !== sanitizedOptions &&
            !isNil(value)
        ) {
            const values = sanitizedOptions.map(option => option.value);
            if (multi && Array.isArray(value)) {
                const invalids = value.filter(v => !values.includes(v));
                if (invalids.length) {
                    setProps({value: without(invalids, value)});
                }
            } else {
                if (!values.includes(value)) {
                    setProps({value: null});
                }
            }
            setOptionsCheck(sanitizedOptions);
        }
    }, [sanitizedOptions, optionsCheck, multi, value]);

    return (
        <div
            id={id}
            className="dash-dropdown"
            style={style}
            data-dash-is-loading={
                (loading_state && loading_state.is_loading) || undefined
            }
        >
            <ReactDropdown
                filterOptions={filterOptions}
                options={sanitizeOptions(options)}
                value={value}
                onChange={onChange}
                onInputChange={onInputChange}
                backspaceRemoves={clearable}
                deleteRemoves={clearable}
                inputProps={{autoComplete: 'off'}}
                {...pick(RDProps, props)}
            />
        </div>
    );
};

Dropdown.propTypes = propTypes;
Dropdown.defaultProps = defaultProps;

export default Dropdown;
