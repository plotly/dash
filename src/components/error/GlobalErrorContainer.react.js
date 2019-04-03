import {connect} from 'react-redux';
import React, {Component} from 'react';
import PropTypes from 'prop-types';
import Radium from 'radium';
import {isEmpty} from 'ramda';
import {resolveError} from '../../actions';
import './werkzeug.css';
import {DebugMenu} from './menu/DebugMenu.react';

class UnconnectedGlobalErrorContainer extends Component {
    constructor(props) {
        super(props);
    }

    resolveError(dispatch, type, myId) {
        if (type === 'backEnd') {
            dispatch(resolveError({type}));
            // dispatch(revert);
        } else {
            dispatch(resolveError({myId, type}));
        }
    }

    render() {
        const {error, dispatch} = this.props;
        return (
            <div id="_dash-global-error-container">
                <DebugMenu
                    errors={error}
                    dispatch={dispatch}
                    resolveError={this.resolveError}
                >
                    <div id="_dash-app-content">{this.props.children}</div>
                </DebugMenu>
            </div>
        );
    }
}

UnconnectedGlobalErrorContainer.propTypes = {
    children: PropTypes.object,
    error: PropTypes.object,
    dispatch: PropTypes.func,
};

const GlobalErrorContainer = connect(
    state => ({
        error: state.error,
    }),
    dispatch => ({dispatch})
)(Radium(UnconnectedGlobalErrorContainer));

export default GlobalErrorContainer;
