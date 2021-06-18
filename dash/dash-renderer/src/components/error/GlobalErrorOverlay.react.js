import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {concat} from 'ramda';

import './GlobalErrorOverlay.css';
import {FrontEndErrorContainer} from './FrontEnd/FrontEndErrorContainer.react';

export default class GlobalErrorOverlay extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        const {visible, error, errorsOpened, clickHandler} = this.props;

        let frontEndErrors;
        if (errorsOpened) {
            const errors = concat(error.frontEnd, error.backEnd);

            frontEndErrors = (
                <FrontEndErrorContainer
                    errors={errors}
                    connected={error.backEndConnected}
                    errorsOpened={errorsOpened}
                    clickHandler={clickHandler}
                />
            );
        }
        return (
            <div>
                <div>{this.props.children}</div>
                <div className='dash-error-menu'>
                    <div className={visible ? 'dash-fe-errors' : ''}>
                        {frontEndErrors}
                    </div>
                </div>
            </div>
        );
    }
}

GlobalErrorOverlay.propTypes = {
    children: PropTypes.object,
    visible: PropTypes.bool,
    error: PropTypes.object,
    errorsOpened: PropTypes.any,
    clickHandler: PropTypes.func
};
