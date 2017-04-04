import {connect} from 'react-redux';
import React, {PropTypes} from 'react';
import {merge} from 'ramda';
import {redo, undo} from '../../actions/index.js';
import Radium from 'radium';


function UnconnectedToolbar(props) {
    const {dispatch, history} = props;
    const styles={
        parentSpanStyle: {
            display: 'inline-block'
        },
        iconStyle: {
            fontSize: 20
        },
        labelStyle: {
            fontSize: 15
        }
    }

    const undoLink = (
        <span
            style={merge({
                'color': history.past.length ? '#0074D9' : 'grey',
                'cursor': history.past.length ? 'pointer' : 'default'
            }, styles.parentSpanStyle)}
            onClick={() => dispatch(undo())}
        >
            <div style={merge(
                {transform: 'rotate(270deg)'},
                styles.iconStyle
            )}>
                {'↺'}
            </div>
            <div style={styles.labelStyle}>
                undo
            </div>
        </span>
    );

    const redoLink = (
        <span
            style={merge({
                'color': history.future.length ? '#0074D9' : 'grey',
                'cursor': history.future.length ? 'pointer' : 'default',
                'marginLeft': 10
            }, styles.parentSpanStyle)}
            onClick={() => dispatch(redo())}
        >
        <div style={merge(
            {transform: 'rotate(90deg)'},
            styles.iconStyle
        )}>
                {'↻'}
            </div>
            <div style={styles.labelStyle}>
                redo
            </div>
        </span>
    );

    return (
        <div style={{
            'position': 'fixed',
            'bottom': '30px',
            'left': '30px',
            'fontSize': '20px',
            'textAlign': 'center',
            'zIndex': '9999',
            'backgroundColor': 'rgba(255, 255, 255, 0.9)',
            'opacity': '0.2',
            ':hover': {
                'opacity': 1
            }
        }}>
            <div style={{
                'position': 'relative'
            }}>
                {history.past.length > 0 ? undoLink : null}
                {history.future.length > 0 ? redoLink : null}
            </div>
        </div>
    );
}

UnconnectedToolbar.propTypes = {
    history: PropTypes.object,
    dispatch: PropTypes.function
};

const Toolbar = connect(
    state => ({
        history: state.history
    }),
    dispatch => ({dispatch})
)(Radium(UnconnectedToolbar));

export default Toolbar;
