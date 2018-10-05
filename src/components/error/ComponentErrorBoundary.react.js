import {connect} from 'react-redux';
import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { revert } from '../../actions/index';
import Radium from 'radium';
import { contains, pluck, find, propEq } from 'ramda';
import uniqid from 'uniqid';
import ComponentErrorOverlay from './ComponentErrorOverlay.react';
import { onError, resolveError } from '../../actions';

class UnconnectedComponentErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      oldChildren: (<div>Initial State</div>),
      myId: uniqid()
    };
  }

  componentDidCatch(error, info) {
    const { dispatch } = this.props;
    dispatch(onError({
      type: 'frontEnd',
      error,
      info,
      myId: this.state.myId
    }));
    this.setState({
      hadError: true,
      error,
      info
    });
  }

  componentDidUpdate(prevProps, prevState) {
    if (!this.state.hadError &&
        this.props != prevProps) {
      this.setState({
        oldChildren: prevProps.children
      });
    }
  }

  resolveError(dispatch, myId) {
    dispatch(resolveError({type: 'frontEnd', myId}))
  }

  render() {
    const { componentType, componentId, dispatch, error } = this.props;
    if (contains(this.state.myId, pluck('myId')(error.frontEnd))) {
      return (
        <ComponentErrorOverlay
           oldChildren={this.state.oldChildren}
           error={find(propEq('myId', this.state.myId))(error.frontEnd).error}
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
    state => ({
      error: state.error
    }),
    dispatch => ({dispatch})
)(Radium(UnconnectedComponentErrorBoundary));

export default ComponentErrorBoundary;
