import React, { Component } from 'react';
import PropTypes from 'prop-types';

export default class ComponentErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hadError: false, error: {}, info: {} };
  }

  componentDidCatch(error, info) {
    this.setState({
      hadError: true,
      error,
      info
    });
  }

  render() {
    const { type, id } = this.props;
    if (this.state.hadError) {
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
    children: PropTypes.object,
    id: PropTypes.string,
    type: PropTypes.string
}
