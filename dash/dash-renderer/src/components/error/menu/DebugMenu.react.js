import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {concat} from 'ramda';

import './DebugMenu.css';

import CheckIcon from '../icons/CheckIcon.svg';
import ClockIcon from '../icons/ClockIcon.svg';
import ErrorIcon from '../icons/ErrorIcon.svg';
import GraphIcon from '../icons/GraphIcon.svg';
import OffIcon from '../icons/OffIcon.svg';

import {CallbackGraphContainer} from '../CallbackGraph/CallbackGraphContainer.react';
import {FrontEndErrorContainer} from '../FrontEnd/FrontEndErrorContainer.react';

const classes = (base, variant, variant2) =>
    `${base} ${base}--${variant}` + (variant2 ? ` ${base}--${variant2}` : '');

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

function shouldShowUpgradeNotification(currentDashVersion, newDashVersion) {
    const lastDismissed = localStorage.getItem('lastDismissed');
    const lastDismissedVersion = localStorage.getItem('lastDismissedVersion');

    if (
        currentDashVersion == newDashVersion ||
        localStorage.getItem('noNotifications') ||
        newDashVersion === undefined
    ) {
        return false;
    } else if (
        lastDismissed &&
        Date.now() - Number(lastDismissed) > 7 * 24 * 60 * 60 * 1000
    ) {
        return true;
    } else if (lastDismissedVersion) {
        return (
            compareVersions(
                localStorage.getItem('lastDismissedVersion'),
                newDashVersion
            ) < 0
        );
    } else {
        return true;
    }
}

async function requestDashVersionInfo(currentDashVersion) {
    return fetch('https://dash-version.plotly.com:8080/sample', {
        method: 'POST',
        body: JSON.stringify({
            dash_version: currentDashVersion
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => response.json());
}

class DebugMenu extends Component {
    constructor(props) {
        super(props);
        const {config} = props;

        requestDashVersionInfo(config.dash_version).then(body => {
            this.setState({...this.state, upgradeInfo: body});
        });

        this.state = {
            opened: false,
            popup: 'errors',
            upgradeInfo: []
        };

        // Close the upgrade tooltip if the user clicks outside of it
        document.addEventListener('click', e => {
            if (
                this.state.upgradeTooltipOpened &&
                !e.target.closest('.dash-debug-menu__upgrade-button')
            ) {
                this.setState({upgradeTooltipOpened: false});
            }
        });
    }

    render() {
        const {popup, upgradeInfo, upgradeTooltipOpened} = this.state;
        const {error, hotReload, config} = this.props;

        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const setDontShowAgain = i => {
            // Set local storage to record the last dismissed notification
            localStorage.setItem('noNotifications', true);
            this.setState({upgradeTooltipOpened: false});
        };

        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const setRemindMeLater = i => {
            // Set local storage to record the last dismissed notification
            localStorage.setItem('lastDismissed', Date.now());
            this.setState({upgradeTooltipOpened: false});
        };

        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const setSkipThisVersion = i => {
            // Set local storage to record the last dismissed version
            localStorage.setItem(
                'lastDismissedVersion',
                upgradeInfo[i].version
            );
            this.setState({upgradeTooltipOpened: false});
        };

        const newDashVersion = upgradeInfo[0]
            ? upgradeInfo[0].version
            : undefined;

        const errCount = error.frontEnd.length + error.backEnd.length;
        const connected = error.backEndConnected;

        const toggleErrors = () => {
            this.setState({popup: popup == 'errors' ? null : 'errors'});
        };

        const toggleCallbackGraph = () => {
            this.setState({
                popup: popup == 'callbackGraph' ? null : 'callbackGraph'
            });
        };

        const toggleShowUpgradeTooltip = () => {
            this.setState({
                upgradeTooltipOpened: !upgradeTooltipOpened
            });
        };

        const errors = concat(error.frontEnd, error.backEnd);

        const _StatusIcon = hotReload
            ? connected
                ? CheckIcon
                : OffIcon
            : ClockIcon;

        const menuContent = (
            <div className='dash-debug-menu__content'>
                {popup == 'callbackGraph' ? <CallbackGraphContainer /> : null}
                <button
                    onClick={toggleErrors}
                    className={
                        (popup == 'errors'
                            ? 'dash-debug-menu__button--selected'
                            : null) + ' dash-debug-menu__button'
                    }
                >
                    <ErrorIcon className='dash-debug-menu__icon' />
                    Errors
                    {errCount > 0 ? (
                        <span className='dash-debug-menu__error-count'>
                            {errCount}
                        </span>
                    ) : null}
                </button>
                <button
                    onClick={toggleCallbackGraph}
                    className={
                        (popup == 'callbackGraph'
                            ? 'dash-debug-menu__button--selected'
                            : '') + ' dash-debug-menu__button'
                    }
                >
                    <GraphIcon className='dash-debug-menu__icon' />
                    Callbacks
                </button>
                <div className='dash-debug-menu__divider' />
                <div className='dash-debug-menu__version'>
                    {this.state.upgradeTooltipOpened ? (
                        <div className='dash-debug-menu__upgrade-tooltip'>
                            <a
                                target='_blank'
                                href='https://dash.plotly.com/installation'
                            >
                                Read details
                            </a>
                            <button onClick={setSkipThisVersion}>
                                Skip this version
                            </button>
                            <button onClick={setRemindMeLater}>
                                Remind me tomorrow
                            </button>
                            <button onClick={setDontShowAgain}>
                                Silence all version notifications
                            </button>
                        </div>
                    ) : null}
                    <span>v{config.dash_version}</span>
                    {shouldShowUpgradeNotification(
                        config.dash_version,
                        newDashVersion
                    ) ? (
                        <button
                            className='dash-debug-menu__upgrade-button'
                            onClick={toggleShowUpgradeTooltip}
                        >
                            Dash update available - v{newDashVersion}
                        </button>
                    ) : null}
                </div>
                <div className='dash-debug-menu__divider' />
                <div className='dash-debug-menu__status'>
                    Server
                    <_StatusIcon className='dash-debug-menu__icon' />
                </div>
            </div>
        );

        return (
            <div>
                <div className={classes('dash-debug-menu__outer')}>
                    {popup == 'errors' && errCount > 0 ? (
                        <FrontEndErrorContainer
                            clickHandler={toggleErrors}
                            errors={errors}
                            connected={error.backEndConnected}
                        />
                    ) : undefined}
                    {menuContent}
                </div>
                {this.props.children}
            </div>
        );
    }
}

DebugMenu.propTypes = {
    children: PropTypes.object,
    error: PropTypes.object,
    hotReload: PropTypes.bool,
    config: PropTypes.object
};

export {DebugMenu};
