import {connect} from 'react-redux';
import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { revert } from '../../actions/index';
import Radium from 'radium';
import ComponentErrorOverlay from './ComponentErrorOverlay.react';

const defaultError = {
  hadError: false,
  error: {},
  info: {}
}

class UnconnectedComponentErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {oldChildren: props.children, ...defaultError};
  }

  componentDidCatch(error, info) {
    this.setState({
      hadError: true,
      error,
      info
    });
  }

  componentDidUpdate(prevProps, prevState) {
    if (!this.state.hadError &&
        prevState.oldChildren !== prevProps.children &&
        prevProps.children !== this.props.children) {
      this.setState({
        oldChildren: prevProps.children
      });
    }
  }

  resolveError(dispatch) {
    dispatch(revert());
    this.setState(defaultError);
  }

  render() {
    const { componentType, componentId, dispatch } = this.props;
    if (this.state.hadError) {
      return (
        <ComponentErrorOverlay
           oldChildren={this.state.oldChildren}
           error={this.state.error}
           componentId={componentId}
           componentType={componentType}
           resolve={() => this.resolveError(dispatch)}
        />
      )
    }
    return this.props.children;
  }
}

UnconnectedComponentErrorBoundary.propTypes = {
    children: PropTypes.object,
    componentId: PropTypes.string,
    componentType: PropTypes.string,
    dispatch: PropTypes.func
}

const ComponentErrorBoundary = connect(
    dispatch => ({dispatch})
)(Radium(UnconnectedComponentErrorBoundary));

export default ComponentErrorBoundary;
