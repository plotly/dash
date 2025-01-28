import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {concat} from 'ramda';

import './DebugMenu.css';

import CheckIcon from '../icons/CheckIcon.svg';
import ClockIcon from '../icons/ClockIcon.svg';
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
            callbackGraphOpened: false,
            errorsOpened: true,
            upgradeInfo: []
        };
    }

    render() {
        const {callbackGraphOpened, errorsOpened, upgradeInfo} = this.state;
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
            this.setState({
                errorsOpened: callbackGraphOpened ? true : !errorsOpened,
                callbackGraphOpened: false
            });
        };

        const toggleCallbackGraph = () => {
            this.setState({callbackGraphOpened: !callbackGraphOpened});
        };

        const toggleShowUpgradeTooltip = () => {
            this.setState({
                upgradeTooltipOpened: !this.state.upgradeTooltipOpened
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
                {callbackGraphOpened ? <CallbackGraphContainer /> : null}
                <button
                    onClick={toggleErrors}
                    className={
                        (!callbackGraphOpened && errorsOpened
                            ? 'dash-debug-menu__button--selected'
                            : null) + ' dash-debug-menu__button'
                    }
                >
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
                        (callbackGraphOpened
                            ? 'dash-debug-menu__button--selected'
                            : null) + ' dash-debug-menu__button'
                    }
                >
                    Callbacks
                </button>
                <div className='dash-debug-menu__divider' />
                <div style={{position: 'relative'}}>
                    {this.state.upgradeTooltipOpened ? (
                        <div className='dash-debug-menu__upgrade-tooltip'>
                            <button onClick={setSkipThisVersion}>
                                Skip This Version
                            </button>
                            <button onClick={setRemindMeLater}>
                                Remind Me Later
                            </button>
                            <button onClick={setDontShowAgain}>
                                Don't Show Again
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
                            Upgrade to v{newDashVersion}
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
                    {errorsOpened && errCount > 0 ? (
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
