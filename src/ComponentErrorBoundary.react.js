import React, { Component } from 'react';
import PropTypes from 'prop-types';

export default class ComponentErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: false };
  }

  componentDidCatch(error, info) {
    this.setState({ error: true });
  }

  render() {
    const { type, id } = this.props;
    if (this.state.error) {
      return (<span
        style={{
          padding: '10px',
          backgroundColor: 'red'
        }}>{"ERROR! In component with id=" + id + " of type " + type}</span>)
    }
    return this.props.children;
  }
}

ComponentErrorBoundary.propTypes = {
    children: PropTypes.object
}
