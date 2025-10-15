import React, {useEffect, useState} from 'react';
import PropTypes from 'prop-types';
import {concat} from 'ramda';
import {useSelector} from 'react-redux';

import './DebugMenu.css';

import CheckIcon from '../icons/CheckIcon.svg';
import ClockIcon from '../icons/ClockIcon.svg';
import ErrorIcon from '../icons/ErrorIcon.svg';
import GraphIcon from '../icons/GraphIcon.svg';
import OffIcon from '../icons/OffIcon.svg';
import Expand from '../icons/Expand.svg';
import {VersionInfo} from './VersionInfo.react';
import {CallbackGraphContainer} from '../CallbackGraph/CallbackGraphContainer.react';
import {FrontEndErrorContainer} from '../FrontEnd/FrontEndErrorContainer.react';
import ExternalWrapper from '../../../wrapper/ExternalWrapper';
import PlotlyCloud from './PlotlyCloud';
import {DevtoolProvider, useDevtool} from './DevtoolContext';

const classes = (base, variant, variant2) =>
    `${base} ${base}--${variant}` + (variant2 ? ` ${base}--${variant2}` : '');

const isCollapsed = () => {
    try {
        return localStorage.getItem('dash_debug_menu_collapsed') === 'true';
    } catch (e) {
        // If localStorage is not available, default to false
        return false;
    }
};

const MenuContent = ({
    hotReload,
    connected,
    popup,
    toggleErrors,
    errCount,
    toggleCallbackGraph,
    config
}) => {
    const ready = useSelector(state => state.appLifecycle === 'HYDRATED');
    const _StatusIcon = hotReload
        ? connected
            ? CheckIcon
            : OffIcon
        : ClockIcon;

    const status = hotReload
        ? connected
            ? 'available'
            : 'unavailable'
        : 'cold';

    let custom = null;
    if (config.dev_tools?.length && ready) {
        custom = config.dev_tools.reduce(
            (acc, devtool, i) => {
                const comp = (
                    <ExternalWrapper
                        component={devtool}
                        componentPath={['__dash_devtools', i]}
                        key={devtool?.props?.id ? devtool.props.id : i}
                    />
                );
                if (devtool.position === 'left') {
                    acc.left.push(comp);
                } else {
                    acc.right.push(comp);
                }
                return acc;
            },
            {left: [], right: []}
        );
    }

    return (
        <div className='dash-debug-menu__content'>
            {custom && <>{custom.left}</>}
            {!config.plotly_cloud_installed ? <PlotlyCloud /> : null}
            <button
                onClick={toggleErrors}
                className={
                    (popup == 'errors'
                        ? 'dash-debug-menu__button--selected'
                        : null) + ' dash-debug-menu__button'
                }
                id='dash-debug-menu__errors-button'
            >
                <ErrorIcon
                    className='dash-debug-menu__icon'
                    width={16}
                    height={16}
                    fill='currentColor'
                />
                Errors
                {errCount > 0 ? (
                    <span className='test-devtools-error-count dash-debug-menu__error-count'>
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
                id='dash-debug-menu__callback-graph-button'
            >
                <GraphIcon
                    className='dash-debug-menu__icon'
                    width={16}
                    height={16}
                    fill='currentColor'
                />
                Callbacks
            </button>
            <div className='dash-debug-menu__divider' />
            <VersionInfo config={config} />
            <div className='dash-debug-menu__divider' />
            <div
                className={`dash-debug-menu__status dash-debug-menu__button--${status}`}
            >
                Server
                <_StatusIcon className='dash-debug-menu__icon' />
            </div>
            {custom && <>{custom.right}</>}
            <div
                className='dash-debug-menu__divider'
                style={{marginRight: 0}}
            />
        </div>
    );
};

const Debug = ({error, hotReload, config, children}) => {
    const {popup, setPopup} = useDevtool();
    const [collapsed, setCollapsed] = useState(isCollapsed);

    const errCount = error.frontEnd.length + error.backEnd.length;
    const connected = error.backEndConnected;

    useEffect(() => {
        if (errCount > 0 && popup == null) {
            setPopup('errors');
        }
    }, [errCount]);

    const toggleErrors = () => {
        setPopup(popup == 'errors' ? null : 'errors');
    };

    const toggleCallbackGraph = () => {
        setPopup(popup == 'callbackGraph' ? null : 'callbackGraph');
    };

    const toggleCollapsed = () => {
        setCollapsed(!collapsed);
        try {
            localStorage.setItem('dash_debug_menu_collapsed', !collapsed);
        } catch (e) {
            // If localStorage is not available, do nothing
        }
    };

    const errors = concat(error.frontEnd, error.backEnd);

    useEffect(() => {
        if (errors.length && popup !== 'errors') {
            setPopup('errors');
        }
    }, [error]);

    const popupContent = (
        <div className='dash-debug-menu__popup'>
            {popup == 'callbackGraph' ? <CallbackGraphContainer /> : undefined}
            {popup == 'errors' && errCount > 0 ? (
                <FrontEndErrorContainer
                    clickHandler={toggleErrors}
                    errors={errors}
                    connected={error.backEndConnected}
                />
            ) : undefined}
        </div>
    );

    const menuContent = collapsed ? undefined : (
        <MenuContent
            popup={popup}
            errCount={errCount}
            toggleErrors={toggleErrors}
            toggleCallbackGraph={toggleCallbackGraph}
            config={config}
            hotReload={hotReload}
            connected={connected}
        />
    );

    return (
        <div>
            <div
                className={classes(
                    'dash-debug-menu__outer',
                    collapsed ? 'collapsed' : 'expanded'
                )}
            >
                {popupContent}
                {menuContent}
                <button
                    onClick={toggleCollapsed}
                    className={classes(
                        'dash-debug-menu__toggle',
                        collapsed ? 'collapsed' : 'expanded'
                    )}
                >
                    <Expand />
                    {errCount > 0 && collapsed ? (
                        <div className='dash-debug-menu__error-indicator' />
                    ) : null}
                </button>
            </div>
            {children}
        </div>
    );
};

const DebugMenu = ({children, ...props}) => {
    return (
        <DevtoolProvider>
            <Debug {...props}>{children}</Debug>
        </DevtoolProvider>
    );
};

DebugMenu.propTypes = {
    children: PropTypes.object,
    error: PropTypes.object,
    hotReload: PropTypes.bool,
    config: PropTypes.object
};

export {DebugMenu};
