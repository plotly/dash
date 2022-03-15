import {isNil, pluck, omit, type, without} from 'ramda';
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

const DELIMITER = ',';

const Dropdown = props => {
    const {
        id,
        clearable,
        multi,
        options,
        setProps,
        style,
        loading_state,
        value,
    } = props;
    const [optionsCheck, setOptionsCheck] = useState(null);
    const [sanitizedOptions, filterOptions] = useMemo(() => {
        const sanitized = sanitizeOptions(options);
        return [
            sanitized,
            createFilterOptions({
                options: sanitized,
                tokenizer: TOKENIZER,
            }),
        ];
    }, [options]);

    const selectedValue = useMemo(
        () => (type(value) === 'Array' ? value.join(DELIMITER) : value),
        [value]
    );

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
        if (optionsCheck !== sanitizedOptions && !isNil(value)) {
            const values = sanitizedOptions.map(option => option.value);
            if (multi && Array.isArray(value)) {
                const invalids = value.filter(v => !values.includes(v));
                if (invalids.length) {
                    setProps({value: without(invalids, value)});
                }
            } else {
                if (!values.includes(selectedValue)) {
                    setProps({value: null});
                }
            }
            setOptionsCheck(sanitizedOptions);
        }
    }, [sanitizedOptions, optionsCheck, multi, value, selectedValue]);

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
                value={selectedValue}
                onChange={onChange}
                onInputChange={onInputChange}
                backspaceRemoves={clearable}
                deleteRemoves={clearable}
                inputProps={{autoComplete: 'off'}}
                {...omit(['setProps', 'value', 'options'], props)}
            />
        </div>
    );
};

Dropdown.propTypes = propTypes;
Dropdown.defaultProps = defaultProps;

export default Dropdown;
