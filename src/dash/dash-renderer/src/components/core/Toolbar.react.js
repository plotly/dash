import {connect} from 'react-redux';
import React from 'react';
import PropTypes from 'prop-types';
import {redo, undo} from '../../actions/index.js';
import './Toolbar.css';

function UnconnectedToolbar(props) {
    const {dispatch, history} = props;

    const undoLink = (
        <span
            key='undoLink'
            className='_dash-undo-redo-link'
            onClick={() => dispatch(undo)}
        >
            <div className='_dash-icon-undo'>↺</div>
            <div className='_dash-undo-redo-label'>undo</div>
        </span>
    );

    const redoLink = (
        <span
            key='redoLink'
            className='_dash-undo-redo-link'
            onClick={() => dispatch(redo)}
        >
            <div className='_dash-icon-redo'>↻</div>
            <div className='_dash-undo-redo-label'>redo</div>
        </span>
    );

    return (
        <div className='_dash-undo-redo'>
            <div>
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
)(UnconnectedToolbar);

export default Toolbar;
