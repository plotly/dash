import React, {Component} from 'react';
import PropTypes from 'prop-types';

import './DebugMenu.css';

import BellIcon from '../icons/BellIcon.svg';
import BellIconGrey from '../icons/BellIconGrey.svg';
import CheckIcon from '../icons/CheckIcon.svg';
import ClockIcon from '../icons/ClockIcon.svg';
import DebugIcon from '../icons/DebugIcon.svg';
import GraphIcon from '../icons/GraphIcon.svg';
import GraphIconGrey from '../icons/GraphIconGrey.svg';
import OffIcon from '../icons/OffIcon.svg';
import WhiteCloseIcon from '../icons/WhiteCloseIcon.svg';

import GlobalErrorOverlay from '../GlobalErrorOverlay.react';
import {CallbackGraphContainer} from '../CallbackGraph/CallbackGraphContainer.react';

class DebugMenu extends Component {
    constructor(props) {
        super(props);

        this.state = {
            opened: false,
            callbackGraphOpened: false,
            errorsOpened: true,
        };
    }
    render() {
        const {opened, errorsOpened, callbackGraphOpened} = this.state;
        const {error, graphs, hotReload} = this.props;

        const menuClasses =
            'dash-debug-menu dash-debug-menu--' +
            (opened ? 'opened' : 'closed');

        const errCount = error.frontEnd.length + error.backEnd.length;
        const connected = error.backEndConnected;

        const toggleOpened = () => {
            this.setState({opened: !opened});
        };
        const toggleGraphOpened = () => {
            this.setState({callbackGraphOpened: !callbackGraphOpened});
        };
        const toggleErrorsOpened = () => {
            this.setState({errorsOpened: !errorsOpened});
        };

        const _GraphIcon = callbackGraphOpened ? GraphIcon : GraphIconGrey;
        const _BellIcon = errorsOpened ? BellIcon : BellIconGrey;
        const status = hotReload
            ? connected
                ? 'available'
                : 'unavailable'
            : 'cold';
        const _StatusIcon = hotReload
            ? connected
                ? CheckIcon
                : OffIcon
            : ClockIcon;

        const btnClasses = enabled =>
            `dash-debug-menu__button ${
                enabled ? 'dash-debug-menu__button--enabled' : ''
            }`;

        const menuContent = opened ? (
            <div className="dash-debug-menu__content">
                {callbackGraphOpened ? (
                    <CallbackGraphContainer graphs={graphs} />
                ) : null}
                <div className="dash-debug-menu__button-container">
                    <div
                        className={btnClasses(callbackGraphOpened)}
                        onClick={toggleGraphOpened}
                    >
                        <_GraphIcon className="dash-debug-menu__icon dash-debug-menu__icon--graph" />
                    </div>
                    <label className="dash-debug-menu__button-label">
                        Callback Graph
                    </label>
                </div>
                <div className="dash-debug-menu__button-container">
                    <div
                        className={btnClasses(errorsOpened)}
                        onClick={toggleErrorsOpened}
                    >
                        <_BellIcon className="dash-debug-menu__icon dash-debug-menu__icon--bell" />
                    </div>
                    <label className="dash-debug-menu__button-label">
                        {(errCount ? '🛑 ' : '') +
                            errCount +
                            ' Error' +
                            (errCount === 1 ? '' : 's')}
                    </label>
                </div>
                <div className="dash-debug-menu__button-container dash-debug-menu__button-container--small">
                    <div
                        className={
                            'dash-debug-menu__indicator dash-debug-menu__indicator--' +
                            status
                        }
                    >
                        <_StatusIcon className="dash-debug-menu__icon--small" />
                    </div>
                </div>
                <div className="dash-debug-menu__button-container">
                    <div
                        className="dash-debug-menu__button dash-debug-menu__button--small"
                        onClick={toggleOpened}
                    >
                        <WhiteCloseIcon className="dash-debug-menu__icon--small" />
                    </div>
                </div>
            </div>
        ) : (
            <DebugIcon className="dash-debug-menu__icon dash-debug-menu__icon--debug" />
        );

        const alertsLabel =
            (errCount || !connected) && !opened ? (
                <div className="dash-debug-alert-label">
                    <div
                        className="dash-debug-alert"
                        onClick={toggleErrorsOpened}
                    >
                        {errCount ? (
                            <div className="dash-debug-error-count">
                                {'🛑 ' + errCount}
                            </div>
                        ) : null}
                        {connected ? null : (
                            <div className="dash-debug-disconnected">🚫</div>
                        )}
                    </div>
                </div>
            ) : null;

        return (
            <div>
                {alertsLabel}
                <div
                    className={menuClasses}
                    onClick={opened ? null : toggleOpened}
                >
                    {menuContent}
                </div>
                <GlobalErrorOverlay
                    error={error}
                    visible={errCount > 0}
                    errorsOpened={errorsOpened}
                >
                    {this.props.children}
                </GlobalErrorOverlay>
            </div>
        );
    }
}

DebugMenu.propTypes = {
    children: PropTypes.object,
    error: PropTypes.object,
    graphs: PropTypes.object,
    hotReload: PropTypes.bool,
};

export {DebugMenu};
