import React, {Component, cloneElement} from 'react';
import {omit} from 'ramda';

export default class DashRendererMock extends Component {
    constructor(props) {
        super(props);
        this.state = {};
        this.setProps = this.setProps.bind(this);
    }

    setProps(newProps) {
        this.setState(newProps);
    }

    render() {
        return cloneElement(this.props.children, {
            ...omit(['children'], this.props),
            ...this.state,
            setProps: this.setProps,
        });
    }
}
