import React, { Component } from 'react';
import PropTypes from 'prop-types';

export default class ComponentErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hadError: false, error: {}, info: {} };
    this.togglePopOver = this.togglePopOver.bind(this);
  }

  componentDidCatch(error, info) {
    this.setState({
      hadError: true,
      popoverOpen: false,
      error,
      info
    });
  }

  togglePopOver() {
    this.setState({
      popoverOpen: !this.state.popoverOpen
    });
  }

  render() {
    const { type, id } = this.props;
    if (this.state.hadError) {
      return (
        <div
          onClick={this.togglePopOver}
          style={{
            padding: '5px',
            backgroundColor: 'rgb(255, 0, 0, .7)',
            border: '1px solid black',
            borderRadius: '2px',
            display: 'inline-block'
          }}>
          <p>{"ERROR!"}</p>
          <div
            style={this.state.popoverOpen ? {'display': 'inline'} : {'display': 'none'}}
            toggle={this.togglePopOver}
          >
            <strong>{"Error in " + type + '(id=' + id + ')'}</strong>
            <p>{this.state.error.name + " -- " + this.state.error.message}</p>
          </div>
        </div>
      )
    }
    return this.props.children;
  }
}

ComponentErrorBoundary.propTypes = {
    children: PropTypes.object,
    id: PropTypes.string,
    type: PropTypes.string
}
