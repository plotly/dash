import React, {Component} from 'react';
import PropTypes from 'prop-types';

import './DebugMenu.css';

import BellIcon from '../icons/BellIcon.svg';
import CheckIcon from '../icons/CheckIcon.svg';
import ClockIcon from '../icons/ClockIcon.svg';
import DebugIcon from '../icons/DebugIcon.svg';
import GraphIcon from '../icons/GraphIcon.svg';
import OffIcon from '../icons/OffIcon.svg';

import GlobalErrorOverlay from '../GlobalErrorOverlay.react';
import {CallbackGraphContainer} from '../CallbackGraph/CallbackGraphContainer.react';

const classes = (base, variant, variant2) =>
    `${base} ${base}--${variant}` + (variant2 ? ` ${base}--${variant2}` : '');

const buttonFactory = (
    enabled,
    buttonVariant,
    toggle,
    _Icon,
    iconVariant,
    label
) => (
    <div className='dash-debug-menu__button-container'>
        <div
            className={classes(
                'dash-debug-menu__button',
                buttonVariant,
                enabled && 'enabled'
            )}
            onClick={toggle}
        >
            <_Icon className={classes('dash-debug-menu__icon', iconVariant)} />
            {label ? (
                <label className='dash-debug-menu__button-label'>{label}</label>
            ) : null}
        </div>
    </div>
);

class DebugMenu extends Component {
    constructor(props) {
        super(props);

        this.state = {
            opened: false,
            callbackGraphOpened: false,
            errorsOpened: true
        };
    }
    render() {
        const {opened, errorsOpened, callbackGraphOpened} = this.state;
        const {error, hotReload} = this.props;

        const errCount = error.frontEnd.length + error.backEnd.length;
        const connected = error.backEndConnected;

        const toggleErrors = () => {
            this.setState({errorsOpened: !errorsOpened});
        };

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

        const menuContent = opened ? (
            <div className='dash-debug-menu__content'>
                {callbackGraphOpened ? <CallbackGraphContainer /> : null}
                {buttonFactory(
                    callbackGraphOpened,
                    'callbacks',
                    () => {
                        this.setState({
                            callbackGraphOpened: !callbackGraphOpened
                        });
                    },
                    GraphIcon,
                    'graph',
                    'Callbacks'
                )}
                {buttonFactory(
                    errorsOpened,
                    'errors',
                    toggleErrors,
                    BellIcon,
                    'bell',
                    errCount + ' Error' + (errCount === 1 ? '' : 's')
                )}
                {buttonFactory(
                    false,
                    status,
                    null,
                    _StatusIcon,
                    'indicator',
                    'Server'
                )}
            </div>
        ) : (
            <div className='dash-debug-menu__content' />
        );

        const alertsLabel =
            (errCount || !connected) && !opened ? (
                <div className='dash-debug-alert-label'>
                    <div className='dash-debug-alert' onClick={toggleErrors}>
                        {errCount ? (
                            <div className='dash-debug-error-count'>
                                {'🛑 ' + errCount}
                            </div>
                        ) : null}
                        {connected ? null : (
                            <div className='dash-debug-disconnected'>🚫</div>
                        )}
                    </div>
                </div>
            ) : null;

        const openVariant = opened ? 'open' : 'closed';

        return (
            <div>
                {alertsLabel}
                <div className={classes('dash-debug-menu__outer', openVariant)}>
                    {menuContent}
                </div>
                <div
                    className={classes('dash-debug-menu', openVariant)}
                    onClick={() => {
                        this.setState({opened: !opened});
                    }}
                >
                    <DebugIcon
                        className={classes('dash-debug-menu__icon', 'debug')}
                    />
                </div>
                <GlobalErrorOverlay
                    error={error}
                    visible={errCount > 0}
                    errorsOpened={errorsOpened}
                    clickHandler={toggleErrors}
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
    hotReload: PropTypes.bool
};

export {DebugMenu};
