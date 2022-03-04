import {isNil, pluck, omit} from 'ramda';
import React, {Component} from 'react';
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


export default class Dropdown extends Component {
    constructor(props) {
        super(props);
        this.state = {
            filterOptions: createFilterOptions({
                options: sanitizeOptions(props.options),
                tokenizer: TOKENIZER,
            }),
        };
    }

    UNSAFE_componentWillReceiveProps(newProps) {
        if (newProps.options !== this.props.options) {
            this.setState({
                filterOptions: createFilterOptions({
                    options: sanitizeOptions(newProps.options),
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
                    {...omit(['setProps', 'value', 'options'], this.props)}
                />
            </div>
        );
    }
}

Dropdown.propTypes = propTypes;
Dropdown.defaultProps = defaultProps;
