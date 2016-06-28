import React, {Component, PropTypes} from 'react';

export default class ExampleComponent extends Component {
    render() {
        const {label} = this.props;

        return (
            <div>ExampleComponent: {label}</div>
        );
    }
}

ExampleComponent.propTypes = {
    /**
     * A label that will be printed when this component is rendered.
     */
    label: PropTypes.string.isRequired
};
