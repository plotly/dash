import React, {Component} from 'react';
import './DebugMenu.css';

import DebugIcon from '../icons/DebugIcon.svg';
import WhiteCloseIcon from '../icons/WhiteCloseIcon.svg';
import BellIcon from '../icons/BellIcon.svg';
import BellIconGrey from '../icons/BellIconGrey.svg';
import GraphIcon from '../icons/GraphIcon.svg';
import GraphIconGrey from '../icons/GraphIconGrey.svg';
import PropTypes from 'prop-types';
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
        const {error, graphs} = this.props;

        const menuClasses = opened
            ? 'dash-debug-menu dash-debug-menu--opened'
            : 'dash-debug-menu dash-debug-menu--closed';

        const errCount = error.frontEnd.length + error.backEnd.length;
        const connected = error.backEndConnected;

        const toggleErrorsOpened = () => {
            this.setState({errorsOpened: !errorsOpened});
        };

        const _GraphIcon = callbackGraphOpened ? GraphIcon : GraphIconGrey;
        const _BellIcon = errorsOpened ? BellIcon : BellIconGrey;

        const menuContent = opened ? (
            <div className="dash-debug-menu__content">
                {callbackGraphOpened ? (
                    <CallbackGraphContainer graphs={graphs} />
                ) : null}
                <div className="dash-debug-menu__button-container">
                    <div
                        className={`dash-debug-menu__button ${
                            callbackGraphOpened
                                ? 'dash-debug-menu__button--enabled'
                                : ''
                        }`}
                        onClick={() =>
                            this.setState({
                                callbackGraphOpened: !callbackGraphOpened,
                            })
                        }
                    >
                        <_GraphIcon className="dash-debug-menu__icon dash-debug-menu__icon--graph" />
                    </div>
                    <label className="dash-debug-menu__button-label">
                        Callback Graph
                    </label>
                </div>
                <div className="dash-debug-menu__button-container">
                    <div
                        className={`dash-debug-menu__button ${
                            errorsOpened
                                ? 'dash-debug-menu__button--enabled'
                                : ''
                        }`}
                        onClick={toggleErrorsOpened}
                    >
                        <_BellIcon className="dash-debug-menu__icon dash-debug-menu__icon--bell" />
                    </div>
                    <label className="dash-debug-menu__button-label">
                        🛑 &nbsp;
                        {errCount + ' Error' + (errCount === 1 ? '' : 's')}
                    </label>
                </div>
                <div className="dash-debug-menu__button-container">
                    <div className="dash-debug-menu__connection">
                        {connected ? '✅' : '🚫'}
                    </div>
                    <label className="dash-debug-menu__button-label">
                        Back End {connected ? 'Connected' : 'Disconnected'}
                    </label>
                </div>
                <div className="dash-debug-menu__button-container">
                    <div
                        className="dash-debug-menu__button dash-debug-menu__button--small"
                        onClick={e => {
                            e.stopPropagation();
                            this.setState({opened: false});
                        }}
                    >
                        <WhiteCloseIcon className="dash-debug-menu__icon--close" />
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
                    onClick={() => this.setState({opened: true})}
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
};

export {DebugMenu};
