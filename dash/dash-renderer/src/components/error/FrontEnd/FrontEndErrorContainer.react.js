import React, {Component} from 'react';
import './FrontEndError.css';
import PropTypes from 'prop-types';
import {FrontEndError} from './FrontEndError.react';

class FrontEndErrorContainer extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        const {errors, connected, errorsOpened, clickHandler} = this.props;
        const errorsLength = errors.length;
        if (errorsLength === 0 || !errorsOpened) {
            return null;
        }

        const inAlertsTray = this.props.inAlertsTray;
        let cardClasses = 'dash-error-card dash-error-card--container';

        const errorElements = errors.map((error, i) => {
            return <FrontEndError e={error} isListItem={true} key={i} />;
        });
        if (inAlertsTray) {
            cardClasses += ' dash-error-card--alerts-tray';
        }
        return (
            <div className={cardClasses}>
                <div className='dash-error-card__topbar'>
                    <div className='dash-error-card__message'>
                        🛑 Errors (
                        <strong className='test-devtools-error-count'>
                            {errorsLength}
                        </strong>
                        ){connected ? null : '\u00a0 🚫 Server Unavailable'}
                    </div>
                    <div
                        className='dash-fe-error__icon-x'
                        onClick={() => clickHandler()}
                    >
                        ×
                    </div>
                </div>
                <div className='dash-error-card__list'>{errorElements}</div>
            </div>
        );
    }
}

FrontEndErrorContainer.propTypes = {
    id: PropTypes.string,
    errors: PropTypes.array,
    connected: PropTypes.bool,
    inAlertsTray: PropTypes.any,
    errorsOpened: PropTypes.any,
    clickHandler: PropTypes.func
};

FrontEndErrorContainer.propTypes = {
    inAlertsTray: PropTypes.any
};

export {FrontEndErrorContainer};
