import R from 'ramda';
import React, {Component, PropTypes} from 'react';
import ReactDropdown from 'react-select';

const DELIMETER = ',';

export default class Dropdown extends Component {
    render() {
        const {id, multi, options, value, setProps} = this.props;
        let selectedValue;
        if (R.type(value) === 'array') {
            selectedValue = value.join(DELIMETER);
        } else {
            selectedValue = value;
        }
        return (
            <div id={id}>
                <ReactDropdown
                    options={options}
                    value={selectedValue}
                    onChange={selectedOption => {
                        if (multi) {
                            const values = R.pluck('value', selectedOption);
                            setProps({value: values});
                        } else {
                            setProps({value: selectedOption.value});
                        }

                    }}
                    {...this.props}
                />
            </div>
        );
    }
}

Dropdown.propTypes = {
    className: PropTypes.string,
    /**
     * If true, the option is disabled
     */
    disabled: PropTypes.bool,

    /**
     * The id of the component
     */
    id: PropTypes.string.isRequired,

    /**
     * If true, the user can select multiple values
     */
    multi: PropTypes.bool,

    options: PropTypes.arrayOf(
        PropTypes.shape({
            disabled: PropTypes.bool,
            label: PropTypes.string,
            value: PropTypes.string
        })
    ),

    /**
     * The grey, default text shown when no option is selected
     */
    placeholder: PropTypes.string,

    /**
     * The value of the input
     */
    value: PropTypes.string, // TODO - or array

    /**
     * Dash-assigned callback that gets fired when the input changes
     */
    setProps: PropTypes.func
};
