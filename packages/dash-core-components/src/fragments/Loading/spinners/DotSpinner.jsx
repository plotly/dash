import React from 'react';
import PropTypes from 'prop-types';

/**
 * Spinner created by Tobias Ahlin, https://github.com/tobiasahlin/SpinKit
 */
const DotSpinner = ({status, color, fullscreen, debug, className, style}) => {
    let debugTitle;
    if (debug) {
        debugTitle = (
            <h3 className="dash-loading-title">
                Loading {status.component_name}
                's {status.prop_name}
            </h3>
        );
    }
    let spinnerClass = fullscreen ? 'dash-spinner-container' : '';
    if (className) {
        spinnerClass += ` ${className}`;
    }
    return (
        <div style={style ? style : {}} className={spinnerClass}>
            {debugTitle}
            <div className="dash-spinner dash-dot-spinner">
                <div className="dash-dot-spinner-bounce1"></div>
                <div className="dash-dot-spinner-bounce2"></div>
                <div className="dash-dot-spinner-bounce3"></div>
                </div>
            <style>
                {`
                .dash-spinner-container {
                    position: fixed;
                    width: 100vw;
                    height: 100vh;
                    top: 0;
                    left: 0;
                    background-color: white;
                    z-index: 99;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                .dash-loading-title {
                    text-align: center;
                }
                .dash-dot-spinner {
                    margin: 1rem auto;
                    width: 70px;
                    text-align: center;
                }

                .dash-dot-spinner > div {
                    width: 18px;
                    height: 18px;
                    background-color: ${color};

                    border-radius: 100%;
                    display: inline-block;
                    -webkit-animation: sk-bouncedelay 1.4s infinite ease-in-out both;
                    animation: sk-bouncedelay 1.4s infinite ease-in-out both;
                }

                .dash-dot-spinner .dash-dot-spinner-bounce1 {
                    -webkit-animation-delay: -0.32s;
                    animation-delay: -0.32s;
                }

                .dash-dot-spinner .dash-dot-spinner-bounce2 {
                    -webkit-animation-delay: -0.16s;
                    animation-delay: -0.16s;
                }

                @-webkit-keyframes sk-bouncedelay {
                    0%, 80%, 100% { -webkit-transform: scale(0) }
                    40% { -webkit-transform: scale(1.0) }
                }

                @keyframes sk-bouncedelay {
                    0%, 80%, 100% {
                    -webkit-transform: scale(0);
                    transform: scale(0);
                    } 40% {
                    -webkit-transform: scale(1.0);
                    transform: scale(1.0);
                    }
                }
            `}
            </style>
        </div>
    );
};

DotSpinner.propTypes = {
    status: PropTypes.object,
    color: PropTypes.string,
    className: PropTypes.string,
    fullscreen: PropTypes.bool,
    style: PropTypes.object,
    debug: PropTypes.bool,
};

export default DotSpinner;
