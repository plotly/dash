import React, {Component, PropTypes} from 'react';

/*
 * A controlled input that calls `notifyObservers` on changes.
 */
export default class InputControl extends Component {
    constructor() {
        super();
        this.state = {
            value: ''
        }
    }

    handleChange(value) {
        this.setState({value});
        /**
         * TODO (#22): Remove conditional. Always pass a callback function
         * to components that can change value.
         */
        if (this.props.notifyObservers) {
            this.props.notifyObservers({value})
        }
    }

    render() {
        return (
            <input
                value={this.state.value}
                onChange={e => this.handleChange(e.target.value)}
                {...this.props}
            />
        );
    }
}

InputControl.propTypes = {

    /**
     * Function that updates the state tree.
     * Passed in from renderer IF the component has observers.
     * TODO (#22): Always pass a callback function to components that can change
     * value.
     */
    notifyObservers: PropTypes.func
};
