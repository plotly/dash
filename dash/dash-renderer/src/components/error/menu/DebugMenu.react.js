import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {concat} from 'ramda';

import './DebugMenu.css';

import CheckIcon from '../icons/CheckIcon.svg';
import ClockIcon from '../icons/ClockIcon.svg';
import ErrorIcon from '../icons/ErrorIcon.svg';
import GraphIcon from '../icons/GraphIcon.svg';
import OffIcon from '../icons/OffIcon.svg';
import {VersionInfo} from './VersionInfo.react';
import {CallbackGraphContainer} from '../CallbackGraph/CallbackGraphContainer.react';
import {FrontEndErrorContainer} from '../FrontEnd/FrontEndErrorContainer.react';

const classes = (base, variant, variant2) =>
    `${base} ${base}--${variant}` + (variant2 ? ` ${base}--${variant2}` : '');

const MenuContent = ({
    hotReload,
    connected,
    popup,
    toggleErrors,
    errCount,
    toggleCallbackGraph,
    config
}) => {
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

    return (
        <div className='dash-debug-menu__content'>
            <button
                onClick={toggleErrors}
                className={
                    (popup == 'errors'
                        ? 'dash-debug-menu__button--selected'
                        : null) + ' dash-debug-menu__button'
                }
                id='dash-debug-menu__errors-button'
            >
                <ErrorIcon className='dash-debug-menu__icon' />
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
                <GraphIcon className='dash-debug-menu__icon' />
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
        </div>
    );
};

class DebugMenu extends Component {
    constructor(props) {
        super(props);

        this.state = {
            opened: false,
            popup: 'errors'
        };

        // Bind the resize listener to the instance
        this.resizeListener = this.resizeListener.bind(this);

        // Add the resize event listener
        window.addEventListener('resize', this.resizeListener);


    }

    resizeListener() {
        const el = window.document.querySelector('#_dash-global-error-container')
        if (el && !el.classList.contains('hide-dash-debug-console')) {
            // Recalculate size on resize
            this.calcSize();
        }
    }

    calcSize() {
        const totalHeight = window.innerHeight;
        const clearance = 40; // Desired clearance in pixels
        const usableHeight = totalHeight - clearance;

        // Assuming the original content height is the full window height
        const originalHeight = totalHeight;
        const scaleFactor = usableHeight / originalHeight;

        // Apply scaling using transform
        const contentElement = document.querySelector('body');
        if (contentElement) {
            contentElement.style.transform = `scale(1, ${scaleFactor})`;
            contentElement.style.transformOrigin = 'left top'; // Scale from the top
            contentElement.style.height = '100vh';
            contentElement.style.width = '100vw';
            contentElement.style.overflowX = 'hidden';
        }
    }

    componentDidMount() {
        // Trigger the resize event manually when the component mounts
        this.resizeListener();
    }

    render() {
        const {popup} = this.state;
        const {error, hotReload, config} = this.props;
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

        const errors = concat(error.frontEnd, error.backEnd);

        const popupContent = (
            <div className='dash-debug-menu__popup'>
                {popup == 'callbackGraph' ? (
                    <CallbackGraphContainer />
                ) : undefined}
                {popup == 'errors' && errCount > 0 ? (
                    <FrontEndErrorContainer
                        clickHandler={toggleErrors}
                        errors={errors}
                        connected={error.backEndConnected}
                    />
                ) : undefined}
            </div>
        );

        const menuContent = (
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

        const toggleDebugTools = () => {
            const el = window.document.querySelector('#_dash-global-error-container')
            if (el) {
                el.classList.toggle('hide-dash-debug-console')
                if (el.classList.contains('hide-dash-debug-console')) {
                    const contentElement = document.querySelector('body');
                    contentElement.style.transform = ''
                    contentElement.style.transformsOrigin = ''
                    contentElement.style.overflowX = ''
                } else {
                    this.calcSize()
                }
            }
        }

        return (
            <div className='debug-tool-holder'>
                <div className={classes('dash-debug-menu__outer')}>
                    {popupContent}
                    {menuContent}
                </div>
                <button
                    className='display-debug-toggle'
                    onClick={toggleDebugTools}
                    >
                    {errCount > 0 ? (
                        <span className='test-devtools-error-count dash-debug-menu__error-count'>
                            {errCount}
                        </span>
                    ) : null}
                </button>
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
