import {connect} from 'react-redux';
import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { revert, resolveError } from '../../actions/index';
import Radium from 'radium';
import GlobalErrorOverlay from './GlobalErrorOverlay.react';
import serverErrorCSS from './werkzueg.css';

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
    if (error.backEnd.errorPage) {
      return (
        <div>
          <img
            style={{"display": "none"}}
            src="http://placehold.it/1x1"
            onLoad={(
              function() {
                var newWin = open('error.html','werkzueg','height=1024,width=1280');
                newWin.document.write(error.backEnd.errorPage);
                var debugger_css = newWin.document.getElementsByTagName('link')[0];
                debugger_css.parentNode.removeChild(debugger_css);
                var style = newWin.document.createElement('style');
                style.type = 'text/css';
                style.innerHTML = serverErrorCSS;
                newWin.document.getElementsByTagName('head')[0].appendChild(style);
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
