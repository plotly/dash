import React, { Component } from 'react';
import PropTypes from 'prop-types';
import io from 'socket.io-client'

const ErrorDisplay = ({ errorOrigin, errorType, errorMessage, errorTraceback }) => (
  <div>
    <h1> Dash had an error in the {errorOrigin}.</h1>
    <h3>{errorType}</h3>
    <h5>{errorMessage}</h5>
    <code>
      {errorTraceback.split("\n").map(line => (<div>{line}</div>))}
    </code>
  </div>
)

export default class ErrorHandler extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: {}
    };
  }

  componentDidCatch(error, info) {
    this.setState({
      hasError: true,
      error: {
        errorOrigin: 'front-end',
        errorType: error.name,
        errorMessage: error.message,
        errorTraceback: info.componentStack
      }
    });
  }

  componentWillMount() {
    let connectionString = 'http://' + document.domain + ':' + location.port + '/_dash-errors';
    let socket = io.connect(connectionString);
    socket.on('error', function(error) {
      this.setState({
        hasError: true,
        error: {errorOrigin: 'back-end', ...error}
      })
    }.bind(this));
  }

  render() {
    return this.state.hasError ? (
      <ErrorDisplay {...this.state.error} />
    ) : this.props.children;
  }
}

ErrorHandler.propTypes = {
    children: PropTypes.object
}
