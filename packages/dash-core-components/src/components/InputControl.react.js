import React, {Component, PropTypes} from 'react';

/*
 * A controlled input that calls `valueChanged` on changes.
 */
export default class InputControl extends Component {
    constructor() {
        super()
        this.state = {
            value: ''
        }
    }

    handleChange(value) {
        this.setState({value});
        this.props.valueChanged({value});
    }

    render() {
        return (
            <input
                value={this.state.value}
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
    valueChanged: PropTypes.func
};

InputControl.defaultProps = {
    valueChanged: () => {}
};
