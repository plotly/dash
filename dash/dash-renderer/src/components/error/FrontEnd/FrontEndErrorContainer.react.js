import React, {Component} from 'react';
import './FrontEndError.css';
import PropTypes from 'prop-types';
import {FrontEndError} from './FrontEndError.react';

const DAY_IN_MS = 86400000;

function compareVersions(v1, v2) {
    const v1Parts = v1.split('.').map(Number);
    const v2Parts = v2.split('.').map(Number);

    for (let i = 0; i < Math.max(v1Parts.length, v2Parts.length); i++) {
        const part1 = v1Parts[i] || 0;
        const part2 = v2Parts[i] || 0;

        if (part1 > part2) return 1;
        if (part1 < part2) return -1;
    }

    return 0;
}

class FrontEndErrorContainer extends Component {
    constructor(props) {
        super(props);

        const {config} = props;

        if (!localStorage.getItem('noNotifications')) {
            fetch('https://dash-version.plotly.com:8080/sample', {
                method: 'POST',
                body: JSON.stringify({
                    dash_version: config.dash_version
                }),
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(response => {
                response.json().then(body => {
                    this.setState({...this.state, notificationInfo: body});
                });
            });
        }

        this.state = {
            dismissed: [false * this.props.errors.length],
            notificationInfo: []
        };
    }

    render() {
        const {errors, errorsOpened} = this.props;
        const {dismissed, notificationInfo} = this.state;
        const errorsLength = errors.length;

        if (
            (errorsLength === 0 || !errorsOpened) &&
            notificationInfo.length === 0
        ) {
            return null;
        }

        const inAlertsTray = this.props.inAlertsTray;
        let cardClasses = 'dash-error-card dash-error-card--container';

        const errorElements = errors.map((error, i) => {
            if (dismissed[i]) {
                return null;
            }
            return (
                <FrontEndError
                    e={error}
                    isListItem={true}
                    key={i}
                    onDismiss={() => {
                        dismissed[i] = true;
                        this.setState({dismissed: dismissed});
                    }}
                />
            );
        });

        const setDontShowAgain = i => {
            // Set local storage to record the last dismissed notification
            localStorage.setItem('noNotifications', true);

            dismissed[errorsLength + i] = true;
            this.setState({dismissed: dismissed});
        };

        const setRemindMeLater = i => {
            // Set local storage to record the last dismissed notification
            localStorage.setItem('lastDismissed', Date.now());

            dismissed[errorsLength + i] = true;
            this.setState({dismissed: dismissed});
        };

        const setSkipThisVersion = i => {
            // Set local storage to record the last dismissed version
            localStorage.setItem(
                'lastDismissedVersion',
                notificationInfo[i].version
            );

            dismissed[errorsLength + i] = true;
            this.setState({dismissed: dismissed});
        };

        const notificationElements = notificationInfo.map((notification, i) => {
            const wasDismissedInLastDay =
                Date.now() - localStorage.getItem('lastDismissed') < DAY_IN_MS;
            const lastDismissedVersion = localStorage.getItem(
                'lastDismissedVersion'
            );
            const hasDismissedVersion =
                lastDismissedVersion !== null &&
                compareVersions(lastDismissedVersion, notification.version) ==
                    0;
            if (
                dismissed[errorsLength + i] ||
                wasDismissedInLastDay ||
                hasDismissedVersion ||
                localStorage.getItem('noNotifications')
            ) {
                return null;
            }
            return (
                <div
                    key={`notification-${i}`}
                    className='dash-error-card__list-item'
                    style={{
                        display: 'flex',
                        flexDirection: 'column'
                    }}
                >
                    <p>{notification.message}</p>
                    <div className='dash-notification__buttons'>
                        {notification.buttons.map(button => {
                            switch (button) {
                                case 'dont_show_again':
                                    return (
                                        <button
                                            onClick={() => setDontShowAgain(i)}
                                        >
                                            Don't Show Again
                                        </button>
                                    );
                                case 'remind_me_later':
                                    return (
                                        <button
                                            onClick={() => setRemindMeLater(i)}
                                        >
                                            Remind Me Later
                                        </button>
                                    );
                                case 'skip_this_version':
                                    return (
                                        <button
                                            onClick={() =>
                                                setSkipThisVersion(i)
                                            }
                                        >
                                            Skip This Version
                                        </button>
                                    );
                                default:
                                    return null;
                            }
                        })}
                    </div>
                </div>
            );
        });

        if (inAlertsTray) {
            cardClasses += ' dash-error-card--alerts-tray';
        }

        return (
            <div className={cardClasses}>
                <div className='dash-error-card__list'>
                    {errorElements}
                    {notificationElements}
                </div>
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
    clickHandler: PropTypes.func,
    config: PropTypes.object
};

FrontEndErrorContainer.propTypes = {
    inAlertsTray: PropTypes.any
};

export {FrontEndErrorContainer};
