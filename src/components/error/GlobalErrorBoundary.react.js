import {connect} from 'react-redux';
import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { revert, resolveError } from '../../actions/index';
import Radium from 'radium';

import GlobalErrorOverlay from './GlobalErrorOverlay.react';

class UnconnectedGlobalErrorBoundary extends Component {
  constructor(props) {
    super(props);
  }

  resolveError(dispatch) {
    dispatch(revert());
    dispatch(resolveError());
  }

  render() {
    const { error, dispatch } = this.props;
    if (error.error) {
      return (
        <div>
          <img
            style={{"display": "none"}}
            src="http://placehold.it/1x1"
            onLoad={(
              function() {
                var newWin = open('url','windowName','height=600,width=400');
                newWin.document.write(error.errorPage);
                newWin.document.close();
              })()} />
            <GlobalErrorOverlay resolve={() => this.resolveError(dispatch)}>
              {this.props.children}
            </GlobalErrorOverlay>
          </div>
        )
    }
    return this.props.children;
  }
}

UnconnectedGlobalErrorBoundary.propTypes = {
    children: PropTypes.object,
}

const GlobalErrorBoundary = connect(
    state => ({
      error: state.error
    }),
    dispatch => ({dispatch})
)(Radium(UnconnectedGlobalErrorBoundary));

export default GlobalErrorBoundary;
