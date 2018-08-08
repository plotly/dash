import {connect} from 'react-redux';
import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { undo } from './actions/index';
import Radium from 'radium';

const defaultError = {
  hadError: false,
  error: {},
  info: {}
}

class ErrorComponentOverlay extends Component {
  constructor(props) {
    super(props);
    this.state = {
      popoverOpen: false
    }
    this.togglePopOver = this.togglePopOver.bind(this);
  }

  togglePopOver() {
    this.setState({
      popoverOpen: !this.state.popoverOpen
    });
  }

  render() {
    const { oldChildren, error, componentId, componentType, resolve } = this.props;
    return (
      <div style={{position: 'relative'}}>
        <div
          onClick={this.togglePopOver}
          style={{
            position: 'relative',
            padding: '2px',
            backgroundColor: 'rgb(255, 0, 0, .5)',
            border: '1px solid black',
            borderRadius: '2px',
            display: 'inline-block'
          }}>
          <div style={{position: 'relative', zIndex: -1}}>{oldChildren}</div>
          <div
            style={this.state.popoverOpen ? {'display': 'inline'} : {'display': 'none'}}
            toggle={this.togglePopOver}
          >
            <strong>{"Error in " + componentType + '(id=' + componentId + ')'}</strong>
            <p>{error.name + " -- " + error.message}</p>
            <button onClick={resolve}>Resolve Error</button>
          </div>
        </div>
      </div>
    )
  }
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
    dispatch(undo());
    this.setState(defaultError);
  }

  render() {
    const { type, id, dispatch } = this.props;
    if (this.state.hadError) {
      return (
        <ErrorComponentOverlay
           oldChildren={this.state.oldChildren}
           error={{id, type, ...this.state.error}}
           componentId={id}
           componentType={type}
           resolve={() => this.resolveError(dispatch)}
        />
      )
    }
    return this.props.children;
  }
}

UnconnectedComponentErrorBoundary.propTypes = {
    children: PropTypes.object,
    id: PropTypes.string,
    type: PropTypes.string
}

const ComponentErrorBoundary = connect(
    state => ({}),
    dispatch => ({dispatch})
)(Radium(UnconnectedComponentErrorBoundary));

export default ComponentErrorBoundary;
