import React, {Component} from 'react';
import './FrontEndError.css';
import PropTypes from 'prop-types';
import {FrontEndError} from './FrontEndError.react';

class FrontEndErrorContainer extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        const errorsLength = this.props.errors.length;
        if (errorsLength === 0) {
            return null;
        }

        const inAlertsTray = this.props.inAlertsTray;
        let cardClasses = 'dash-error-card dash-error-card--container';

        const errorElements = this.props.errors.map((error, i) => {
            return <FrontEndError e={error} isListItem={true} key={i} />;
        });
        if (inAlertsTray) {
            cardClasses += ' dash-error-card--alerts-tray';
        }
        return (
            <div className={cardClasses}>
                <div className="dash-error-card__topbar">
                    <div className="dash-error-card__message">
                        🛑 Errors (
                        <strong className="test-devtools-error-count">
                            {errorsLength}
                        </strong>
                        )
                    </div>
                </div>
                <div className="dash-error-card__list">{errorElements}</div>
            </div>
        );
    }
}

FrontEndErrorContainer.propTypes = {
    errors: PropTypes.array,
    inAlertsTray: PropTypes.any,
};

FrontEndErrorContainer.propTypes = {
    inAlertsTray: PropTypes.any,
};

export {FrontEndErrorContainer};
