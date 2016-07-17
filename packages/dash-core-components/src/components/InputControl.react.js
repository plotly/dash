import React, {Component, PropTypes} from 'react';

/*
 * An input that calls `valueChanged` on changes.
 */
export default class InputControl extends Component {
    handleChange(value) {
        this.props.valueChanged({value});
    }

    render() {
        return (
            <input
                value={this.props.value}
                onChange={e => this.handleChange(e.target.value)}
                {...this.props}
            />
        )
    }
}

InputControl.propTypes = {

    /**
     * Function that updates the state tree.
     */
    valueChanged: PropTypes.func,

    /**
     * Initial input value
     */
    value: PropTypes.string
};

InputControl.defaultProps = {
    valueChanged: () => {},
    value: ''
};
