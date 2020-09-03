import {connect} from 'react-redux';
import React from 'react';
import PropTypes from 'prop-types';
import {mergeRight} from 'ramda';
import {redo, undo} from '../../actions/index.js';
import Radium from 'radium';

function UnconnectedToolbar(props) {
    const {dispatch, history} = props;
    const styles = {
        parentSpanStyle: {
            display: 'inline-block',
            opacity: '0.2',
            ':hover': {
                opacity: 1
            }
        },
        iconStyle: {
            fontSize: 20
        },
        labelStyle: {
            fontSize: 15
        }
    };

    const undoLink = (
        <span
            key='undoLink'
            style={mergeRight(
                {
                    color: history.past.length ? '#0074D9' : 'grey',
                    cursor: history.past.length ? 'pointer' : 'default'
                },
                styles.parentSpanStyle
            )}
            onClick={() => dispatch(undo)}
        >
            <div
                style={mergeRight(
                    {transform: 'rotate(270deg)'},
                    styles.iconStyle
                )}
            >
                ↺
            </div>
            <div style={styles.labelStyle}>undo</div>
        </span>
    );

    const redoLink = (
        <span
            key='redoLink'
            style={mergeRight(
                {
                    color: history.future.length ? '#0074D9' : 'grey',
                    cursor: history.future.length ? 'pointer' : 'default',
                    marginLeft: 10
                },
                styles.parentSpanStyle
            )}
            onClick={() => dispatch(redo)}
        >
            <div
                style={mergeRight(
                    {transform: 'rotate(90deg)'},
                    styles.iconStyle
                )}
            >
                ↻
            </div>
            <div style={styles.labelStyle}>redo</div>
        </span>
    );

    return (
        <div
            className='_dash-undo-redo'
            style={{
                position: 'fixed',
                bottom: '30px',
                left: '30px',
                fontSize: '20px',
                textAlign: 'center',
                zIndex: '9999',
                backgroundColor: 'rgba(255, 255, 255, 0.9)'
            }}
        >
            <div
                style={{
                    position: 'relative'
                }}
            >
                {history.past.length > 0 ? undoLink : null}
                {history.future.length > 0 ? redoLink : null}
            </div>
        </div>
    );
}

UnconnectedToolbar.propTypes = {
    history: PropTypes.object,
    dispatch: PropTypes.func
};

const Toolbar = connect(
    state => ({
        history: state.history
    }),
    dispatch => ({dispatch})
)(Radium(UnconnectedToolbar));

export default Toolbar;
