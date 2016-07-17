import React, {Component, PropTypes} from 'react';

/**
 * A component that prints a label value
 */
export default class Label extends Component {
    render() {
        return (
            <label>{this.props.value}</label>
        );
    }
}

Label.propTypes = {

    /**
     * The value of the label
     */
    value: PropTypes.string.isRequired
};
