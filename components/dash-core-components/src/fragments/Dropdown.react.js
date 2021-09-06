import {isNil, pluck, omit, type} from 'ramda';
import React, {Component} from 'react';
import ReactDropdown from 'react-virtualized-select';
import createFilterOptions from 'react-select-fast-filter-options';
import '../components/css/react-virtualized-select@3.1.0.css';
import '../components/css/react-virtualized@9.9.0.css';
import '../components/css/Dropdown.css';

import {propTypes, defaultProps} from '../components/Dropdown.react';

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

const DELIMETER = ',';

export default class Dropdown extends Component {
    constructor(props) {
        super(props);
        this.state = {
            filterOptions: createFilterOptions({
                options: props.options,
                tokenizer: TOKENIZER,
            }),
        };
    }

    UNSAFE_componentWillReceiveProps(newProps) {
        if (newProps.options !== this.props.options) {
            const normalizedOptions = newProps.options.map(opt =>
                type(opt) === 'string'
                    ? {
                          label: opt,
                          value: opt,
                      }
                    : opt
            );
            this.setState({
                filterOptions: createFilterOptions({
                    options: normalizedOptions,
                    tokenizer: TOKENIZER,
                }),
            });
        }
    }

    render() {
        const {
            id,
            clearable,
            multi,
            options,
            setProps,
            style,
            loading_state,
            value,
        } = this.props;
        const {filterOptions} = this.state;
        let selectedValue;
        if (type(value) === 'array') {
            selectedValue = value.join(DELIMETER);
        } else {
            selectedValue = value;
        }
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
                    options={options}
                    value={selectedValue}
                    onChange={selectedOption => {
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
                    }}
                    onInputChange={search_value => setProps({search_value})}
                    backspaceRemoves={clearable}
                    deleteRemoves={clearable}
                    inputProps={{autoComplete: 'off'}}
                    {...omit(['setProps', 'value'], this.props)}
                />
            </div>
        );
    }
}

Dropdown.propTypes = propTypes;
Dropdown.defaultProps = defaultProps;
