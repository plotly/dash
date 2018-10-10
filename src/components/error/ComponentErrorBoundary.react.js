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
      myID: props.componentId,
      myUID: uniqid(),
      oldChildren: (<div>No Initial State</div>)
    };
  }

  componentDidCatch(error, info) {
    const { id, dispatch, children } = this.props;
    dispatch(onError({
      myUID: this.state.myUID,
      myID: this.state.myID,
      type: 'frontEnd',
      error,
      info
    }));
    dispatch(revert());
  }

    }
  }

  resolveError(dispatch, myUID) {
    dispatch(resolveError({type: 'frontEnd', myUID}))
  }

  render() {
    const { componentType, componentId, dispatch, error } = this.props;
    const { myID, myUID } = this.state;
    const hasError = R.contains(myUID, R.pluck('myUID')(error.frontEnd));
    if ( hasError ) {
      const errorToDisplay = R.find(
        R.propEq('myUID', myUID)
      )(error.frontEnd).error;
      return (
        <ComponentErrorOverlay
           error={errorToDisplay}
           componentId={componentId}
           componentType={componentType}
           resolve={() => this.resolveError(dispatch, myUID)}
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
