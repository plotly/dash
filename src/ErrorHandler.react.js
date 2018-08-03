import React, { Component } from 'react';
import PropTypes from 'prop-types';

const FrontEndErrorDisplay = ({ errorOrigin, errorType, errorMessage, errorTraceback }) => (
  <div>
    <h1> Dash had an error in the {errorOrigin}.</h1>
    <h3>{errorType}</h3>
    <h5>{errorMessage}</h5>
    <code>
      {errorTraceback.split("\n").map(line => (<div>{line}</div>))}
    </code>
  </div>
)

FrontEndErrorDisplay.propTypes = {
    errorOrigin: PropTypes.string,
    errorType: PropTypes.string,
    errorMessage: PropTypes.string,
    errorTraceback: PropTypes.string,
}

export default class ErrorHandler extends Component {
  constructor(props) {
    super(props);
    this.state = {
      frontEndError: false,
      error: {}
    };
  }

  componentDidCatch(error, info) {
    this.setState({
      frontEndError: true,
      error: {
        errorOrigin: 'front-end',
        errorType: error.name,
        errorMessage: error.message,
        errorTraceback: info.componentStack
      }
    });
  }

  render() {
    const { error } = this.props;
    if (error.error) {
      return <div dangerouslySetInnerHTML={{__html: error.errorPage}} />
    } else if (this.state.frontEndError) {
      return <FrontEndErrorDisplay {...this.state.error} />
    }
    return this.props.children;
  }
}

ErrorHandler.propTypes = {
    children: PropTypes.object,
    error: PropTypes.object
}
