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
        const {resolve, visible, error, toastsEnabled} = this.props;

        let frontEndErrors;
        if (toastsEnabled) {
            const errors = concat(error.frontEnd, error.backEnd);

            frontEndErrors = (
                <FrontEndErrorContainer errors={errors} resolve={resolve} />
            );
        }
        return (
            <div>
                <div>{this.props.children}</div>
                <div className="dash-error-menu">
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
    resolve: PropTypes.func,
    visible: PropTypes.bool,
    error: PropTypes.object,
    toastsEnabled: PropTypes.any,
};
