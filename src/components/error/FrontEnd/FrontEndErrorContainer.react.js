import React, {Component} from 'react';
import './FrontEndError.css';
import CloseIcon from '../icons/CloseIcon.svg';
import PropTypes from 'prop-types';
import {FrontEndError} from './FrontEndError.react';

class FrontEndErrorContainer extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        const errorsLength = this.props.errors.length;
        const inAlertsTray = this.props.inAlertsTray;
        let cardClasses = 'dash-error-card dash-error-card--container';

        const errorElements = this.props.errors.map(error => {
            return <FrontEndError e={error} isListItem={true} />;
        });
        if (inAlertsTray) {
            cardClasses += ' dash-error-card--alerts-tray';
        }
        return (
            <div className={cardClasses}>
                <div className="dash-error-card__topbar">
                    <h6 className="dash-error-card__message">
                        ⚠️ Alerts (<strong>{errorsLength}</strong> errors)
                    </h6>
                    <CloseIcon
                        className="dash-fe-error__icon-close"
                        onClick={() =>
                            this.props.errors.forEach(error => {
                                this.props.resolve('frontEnd', error.myUID);
                            })
                        }
                    />
                </div>
                <div className="dash-error-card__list">{errorElements}</div>
            </div>
        );
    }
}

FrontEndErrorContainer.propTypes = {
    errors: PropTypes.array,
    resolve: PropTypes.func,
    inAlertsTray: PropTypes.bool,
};

FrontEndErrorContainer.propTypes = {
    inAlertsTray: false,
};

export {FrontEndErrorContainer};
