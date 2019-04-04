import React, {Component} from 'react';
import './DebugMenu.css';

import DebugIcon from '../icons/DebugIcon.svg';
import WhiteCloseIcon from '../icons/WhiteCloseIcon.svg';
import BellIcon from '../icons/BellIcon.svg';
import BellIconGrey from '../icons/BellIconGrey.svg';
import ReloadIcon from '../icons/ReloadIcon.svg';
import GraphIcon from '../icons/GraphIcon.svg';
import WarningIcon from '../icons/WarningIcon.svg';

import PropTypes from 'prop-types';
import {DebugAlertContainer} from './DebugAlertContainer.react';
import GlobalErrorOverlay from '../GlobalErrorOverlay.react';
import {isEmpty} from 'ramda';
import {FrontEndError} from '../FrontEnd/FrontEndError.react';
import {FrontEndErrorContainer} from '../FrontEnd/FrontEndErrorContainer.react';

class DebugMenu extends Component {
    constructor(props) {
        super(props);

        this.state = {
            opened: false,
            alertsOpened: false,
            toastsEnabled: true,
        };
    }
    render() {
        const {opened, alertsOpened, toastsEnabled} = this.state;
        const {errors, resolveError, dispatch} = this.props;

        const menuClasses = opened
            ? 'dash-debug-menu dash-debug-menu--opened'
            : 'dash-debug-menu dash-debug-menu--closed';

        let frontEndErrors;
        if (alertsOpened) {
            if (errors.frontEnd.length > 1) {
                frontEndErrors = (
                    <FrontEndErrorContainer
                        errors={errors.frontEnd}
                        resolve={(type, myId) =>
                            resolveError(dispatch, type, myId)
                        }
                        inAlertsTray={true}
                    />
                );
            } else if (!isEmpty(errors.frontEnd)) {
                const e = errors.frontEnd[0];
                frontEndErrors = (
                    <FrontEndError
                        e={e}
                        resolve={(type, myId) =>
                            resolveError(dispatch, type, myId)
                        }
                        inAlertsTray={true}
                    />
                );
            }
        }

        const menuContent = opened ? (
            <div className="dash-debug-menu__content">
                {frontEndErrors}
                {errors.frontEnd.length > 0 ? (
                    <div className="dash-debug-menu__button-container">
                        <DebugAlertContainer
                            errors={errors.frontEnd}
                            alertsOpened={alertsOpened}
                            onClick={() =>
                                this.setState({alertsOpened: !alertsOpened})
                            }
                        />
                    </div>
                ) : null}
                <div className="dash-debug-menu__button-container">
                    <div className="dash-debug-menu__button">
                        <GraphIcon className="dash-debug-menu__icon dash-debug-menu__icon--graph" />
                    </div>
                    <label className="dash-debug-menu__button-label">
                        Callback Graph
                    </label>
                </div>
                <div className="dash-debug-menu__button-container">
                    <div className="dash-debug-menu__button">
                        <ReloadIcon className="dash-debug-menu__icon" />
                    </div>
                    <label className="dash-debug-menu__button-label">
                        Live Reload
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
                        Notifications
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
            errors.frontEnd.length > 0 && !opened ? (
                <div className="dash-debug-alert-label">
                    <div className="dash-debug-alert">
                        ☣️&nbsp;{errors.frontEnd.length}
                    </div>
                    <div className="dash-debug-alert">
                        <WarningIcon className="dash-debug-alert-container__icon dash-debug-alert-container__icon--warning" />
                        0
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
                    resolve={(type, myId) => resolveError(dispatch, type, myId)}
                    error={errors}
                    visible={
                        !(isEmpty(errors.backEnd) && isEmpty(errors.frontEnd))
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
    errors: PropTypes.object,
    resolveError: PropTypes.function,
    dispatch: PropTypes.function,
};

export {DebugMenu};
