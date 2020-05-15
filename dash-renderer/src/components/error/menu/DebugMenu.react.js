import React, {Component} from 'react';
import {concat, isEmpty} from 'ramda';
import './DebugMenu.css';

import DebugIcon from '../icons/DebugIcon.svg';
import WhiteCloseIcon from '../icons/WhiteCloseIcon.svg';
import BellIcon from '../icons/BellIcon.svg';
import BellIconGrey from '../icons/BellIconGrey.svg';
import GraphIcon from '../icons/GraphIcon.svg';
import GraphIconGrey from '../icons/GraphIconGrey.svg';
import PropTypes from 'prop-types';
import {DebugAlertContainer} from './DebugAlertContainer.react';
import GlobalErrorOverlay from '../GlobalErrorOverlay.react';
import {CallbackGraphContainer} from '../CallbackGraph/CallbackGraphContainer.react';

class DebugMenu extends Component {
    constructor(props) {
        super(props);

        this.state = {
            opened: false,
            alertsOpened: false,
            callbackGraphOpened: false,
            toastsEnabled: true,
        };
    }
    render() {
        const {
            opened,
            alertsOpened,
            toastsEnabled,
            callbackGraphOpened,
        } = this.state;
        const {error, graphs} = this.props;

        const menuClasses = opened
            ? 'dash-debug-menu dash-debug-menu--opened'
            : 'dash-debug-menu dash-debug-menu--closed';

        const menuContent = opened ? (
            <div className="dash-debug-menu__content">
                {callbackGraphOpened ? (
                    <CallbackGraphContainer/>
                ) : null}
                {error.frontEnd.length > 0 || error.backEnd.length > 0 ? (
                    <div className="dash-debug-menu__button-container">
                        <DebugAlertContainer
                            errors={concat(error.frontEnd, error.backEnd)}
                            alertsOpened={alertsOpened}
                            onClick={() =>
                                this.setState({alertsOpened: !alertsOpened})
                            }
                        />
                    </div>
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
                        {callbackGraphOpened ? (
                            <GraphIcon className="dash-debug-menu__icon dash-debug-menu__icon--graph" />
                        ) : (
                            <GraphIconGrey className="dash-debug-menu__icon dash-debug-menu__icon--bell" />
                        )}
                    </div>
                    <label className="dash-debug-menu__button-label">
                        Callback Graph
                    </label>
                </div>
                <div className="dash-debug-menu__button-container">
                    <div
                        className={`dash-debug-menu__button ${
                            toastsEnabled
                                ? 'dash-debug-menu__button--enabled'
                                : ''
                        }`}
                        onClick={() =>
                            this.setState({
                                toastsEnabled: !toastsEnabled,
                            })
                        }
                    >
                        {toastsEnabled ? (
                            <BellIcon className="dash-debug-menu__icon dash-debug-menu__icon--bell" />
                        ) : (
                            <BellIconGrey className="dash-debug-menu__icon dash-debug-menu__icon--bell" />
                        )}
                    </div>
                    <label className="dash-debug-menu__button-label">
                        Errors
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
            error.frontEnd.length + error.backEnd.length > 0 && !opened ? (
                <div className="dash-debug-alert-label">
                    <div className="dash-debug-alert">
                        🛑 &nbsp;{error.frontEnd.length + error.backEnd.length}
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
                    visible={
                        !(isEmpty(error.backEnd) && isEmpty(error.frontEnd))
                    }
                    toastsEnabled={toastsEnabled}
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
