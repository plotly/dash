import {Component, cloneElement} from 'react';
import PropTypes from 'prop-types';
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

DashRendererMock.propTypes = {
    children: PropTypes.any
}
