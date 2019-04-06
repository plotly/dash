import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {isEmpty} from 'ramda';
// import {FrontEndError} from './FrontEnd/FrontEndError.react';
import './GlobalErrorOverlay.css';
import {FrontEndErrorContainer} from './FrontEnd/FrontEndErrorContainer.react';

export default class GlobalErrorOverlay extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        const {resolve, visible, error, toastsEnabled} = this.props;
        // let backEndErrors;
        let frontEndErrors;
        if (toastsEnabled) {
            let errors = [];
            if (error.frontEnd.length) {
                errors = error.frontEnd;
            }
            if (!isEmpty(error.backEnd)) {
                errors.push({error: {
                    message: 'Python exception',
                    html: error.backEnd.errorPage,
                }});
            }
            frontEndErrors = (
                <FrontEndErrorContainer
                    errors={errors}
                    resolve={resolve}
                />
            );
        }
        return (
            <div>
                <div>{this.props.children}</div>
                <div className="dash-error-menu">
                    {isEmpty(error.backEnd) ? null : (
                        <button onClick={() => resolve('backEnd')}>
                            Resolve BackEnd Error
                        </button>
                    )}
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
