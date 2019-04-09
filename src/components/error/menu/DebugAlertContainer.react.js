import './DebugAlertContainer.css';
import {Component} from 'react';
import PropTypes from 'prop-types';
import WarningIconWhite from '../icons/WarningIconWhite.svg';
import ErrorIconWhite from '../icons/ErrorIconWhite.svg';

class DebugAlertContainer extends Component {
    constructor(props) {
        super(props);
    }
    render() {
        const {alertsOpened} = this.props;
        return (
            <div
                className={`dash-debug-alert-container${
                    alertsOpened ? ' dash-debug-alert-container--opened' : ''
                }`}
                onClick={this.props.onClick}
            >
                <div className="dash-debug-alert">
                    {alertsOpened ? (
                        <ErrorIconWhite className="dash-debug-alert-container__icon" />
                    ) : (
                        '☣️'
                    )}
                    {this.props.errors.length}
                </div>
                <div className="dash-debug-alert">
                    {alertsOpened ? (
                        <WarningIconWhite className="dash-debug-alert-container__icon dash-debug-alert-container__icon--warning" />
                    ) : (
                        '⚠️'
                    )}
                    0
                </div>
            </div>
        );
    }
}

DebugAlertContainer.propTypes = {
    errors: PropTypes.object,
    alertsOpened: PropTypes.bool,
    onClick: PropTypes.function,
};

export {DebugAlertContainer};
