import {connect} from 'react-redux';
import React, { Component } from 'react';
import PropTypes from 'prop-types';
import Radium from 'radium';
import { isEmpty } from 'ramda';
import { revert, resolveError } from '../../actions';
import GlobalErrorOverlay from './GlobalErrorOverlay.react';
import serverErrorCSS from './werkzueg.css';

class UnconnectedGlobalErrorBoundary extends Component {
  constructor(props) {
    super(props);
  }

  resolveError(dispatch, type, myId) {
    if (type === 'backEnd'){
      dispatch(resolveError({ type }));
      dispatch(revert());
    } else {
      dispatch(resolveError({ myId, type }));
    }
  }

  serverError(error) {
    var newWin = open('error.html','werkzueg','height=1024,width=1280');
    newWin.document.write(error.backEnd.errorPage);
    var debugger_css = newWin.document.getElementsByTagName('link')[0];
    debugger_css.parentNode.removeChild(debugger_css);
    var style = newWin.document.createElement('style');
    style.type = 'text/css';
    style.innerHTML = serverErrorCSS;
    newWin.document.getElementsByTagName('head')[0].appendChild(style);
    newWin.document.close();
  }

  render() {
    const { error, dispatch } = this.props;
    return (
      <div>
        <img
          style={{"display": "none"}}
          src="http://placehold.it/1x1"
          onLoad={isEmpty(error.backEnd) ? (() => {return;})() :
                                           (() => this.serverError(error))()} />
          <GlobalErrorOverlay
            resolve={(type, myId) => this.resolveError(dispatch, type, myId)}
            error={error}
            visible={!(isEmpty(error.backEnd) &&
                       isEmpty(error.frontEnd))}>
            {this.props.children}
          </GlobalErrorOverlay>
        </div>
      )
  }
}

UnconnectedGlobalErrorBoundary.propTypes = {
    children: PropTypes.object,
    error: PropTypes.object,
    dispatch: PropTypes.func
}

const GlobalErrorBoundary = connect(
    state => ({
      error: state.error
    }),
    dispatch => ({dispatch})
)(Radium(UnconnectedGlobalErrorBoundary));

export default GlobalErrorBoundary;
