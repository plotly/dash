import React from 'react';
import PropTypes from 'prop-types';

/**
 * Spinner created by Tobias Ahlin, https://github.com/tobiasahlin/SpinKit
 */
const CircleSpinner = ({
    status,
    color,
    fullscreen,
    debug,
    className,
    style,
}) => {
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
            <div className="dash-spinner dash-sk-circle">
                <div className="dash-sk-circle1 dash-sk-child" />
                <div className="dash-sk-circle2 dash-sk-child" />
                <div className="dash-sk-circle3 dash-sk-child" />
                <div className="dash-sk-circle4 dash-sk-child" />
                <div className="dash-sk-circle5 dash-sk-child" />
                <div className="dash-sk-circle6 dash-sk-child" />
                <div className="dash-sk-circle7 dash-sk-child" />
                <div className="dash-sk-circle8 dash-sk-child" />
                <div className="dash-sk-circle9 dash-sk-child" />
                <div className="dash-sk-circle10 dash-sk-child" />
                <div className="dash-sk-circle11 dash-sk-child" />
                <div className="dash-sk-circle12 dash-sk-child" />
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
                    .dash-sk-circle {
                        margin: 1rem auto;
                        width: 40px;
                        height: 40px;
                        position: relative;
                    }
                    .dash-sk-circle .dash-sk-child {
                        width: 100%;
                        height: 100%;
                        position: absolute;
                        left: 0;
                        top: 0;
                    }
                    .dash-sk-circle .dash-sk-child:before {
                        content: '';
                        display: block;
                        margin: 0 auto;
                        width: 15%;
                        height: 15%;
                        background-color: ${color};
                        border-radius: 100%;
                        -webkit-animation: dash-sk-circleBounceDelay 1.2s infinite ease-in-out both;
                                animation: dash-sk-circleBounceDelay 1.2s infinite ease-in-out both;
                    }
                    .dash-sk-circle .dash-sk-circle2 {
                        -webkit-transform: rotate(30deg);
                            -ms-transform: rotate(30deg);
                                transform: rotate(30deg); }
                    .dash-sk-circle .dash-sk-circle3 {
                        -webkit-transform: rotate(60deg);
                            -ms-transform: rotate(60deg);
                                transform: rotate(60deg); }
                    .dash-sk-circle .dash-sk-circle4 {
                        -webkit-transform: rotate(90deg);
                            -ms-transform: rotate(90deg);
                                transform: rotate(90deg); }
                    .dash-sk-circle .dash-sk-circle5 {
                        -webkit-transform: rotate(120deg);
                            -ms-transform: rotate(120deg);
                                transform: rotate(120deg); }
                    .dash-sk-circle .dash-sk-circle6 {
                        -webkit-transform: rotate(150deg);
                            -ms-transform: rotate(150deg);
                                transform: rotate(150deg); }
                    .dash-sk-circle .dash-sk-circle7 {
                        -webkit-transform: rotate(180deg);
                            -ms-transform: rotate(180deg);
                                transform: rotate(180deg); }
                    .dash-sk-circle .dash-sk-circle8 {
                        -webkit-transform: rotate(210deg);
                            -ms-transform: rotate(210deg);
                                transform: rotate(210deg); }
                    .dash-sk-circle .dash-sk-circle9 {
                        -webkit-transform: rotate(240deg);
                            -ms-transform: rotate(240deg);
                                transform: rotate(240deg); }
                    .dash-sk-circle .dash-sk-circle10 {
                        -webkit-transform: rotate(270deg);
                            -ms-transform: rotate(270deg);
                                transform: rotate(270deg); }
                    .dash-sk-circle .dash-sk-circle11 {
                        -webkit-transform: rotate(300deg);
                            -ms-transform: rotate(300deg);
                                transform: rotate(300deg); }
                    .dash-sk-circle .dash-sk-circle12 {
                        -webkit-transform: rotate(330deg);
                            -ms-transform: rotate(330deg);
                                transform: rotate(330deg); }
                    .dash-sk-circle .dash-sk-circle2:before {
                        -webkit-animation-delay: -1.1s;
                                animation-delay: -1.1s; }
                    .dash-sk-circle .dash-sk-circle3:before {
                        -webkit-animation-delay: -1s;
                                animation-delay: -1s; }
                    .dash-sk-circle .dash-sk-circle4:before {
                        -webkit-animation-delay: -0.9s;
                                animation-delay: -0.9s; }
                    .dash-sk-circle .dash-sk-circle5:before {
                        -webkit-animation-delay: -0.8s;
                                animation-delay: -0.8s; }
                    .dash-sk-circle .dash-sk-circle6:before {
                        -webkit-animation-delay: -0.7s;
                                animation-delay: -0.7s; }
                    .dash-sk-circle .dash-sk-circle7:before {
                        -webkit-animation-delay: -0.6s;
                                animation-delay: -0.6s; }
                    .dash-sk-circle .dash-sk-circle8:before {
                        -webkit-animation-delay: -0.5s;
                                animation-delay: -0.5s; }
                    .dash-sk-circle .dash-sk-circle9:before {
                        -webkit-animation-delay: -0.4s;
                                animation-delay: -0.4s; }
                    .dash-sk-circle .dash-sk-circle10:before {
                        -webkit-animation-delay: -0.3s;
                                animation-delay: -0.3s; }
                    .dash-spinner-container > .sk-circle .sk-circle11:before {
                        -webkit-animation-delay: -0.2s;
                                animation-delay: -0.2s; }
                    .dash-spinner-container .sk-circle .sk-circle12:before {
                        -webkit-animation-delay: -0.1s;
                                animation-delay: -0.1s; }

                    @-webkit-keyframes dash-sk-circleBounceDelay {
                        0%, 80%, 100% {
                        -webkit-transform: scale(0);
                                transform: scale(0);
                        } 40% {
                        -webkit-transform: scale(1);
                                transform: scale(1);
                        }
                    }

                    @keyframes dash-sk-circleBounceDelay {
                        0%, 80%, 100% {
                        -webkit-transform: scale(0);
                                transform: scale(0);
                        } 40% {
                        -webkit-transform: scale(1);
                                transform: scale(1);
                        }
                    }
            `}
            </style>
        </div>
    );
};

CircleSpinner.propTypes = {
    status: PropTypes.object,
    color: PropTypes.string,
    className: PropTypes.string,
    fullscreen: PropTypes.bool,
    style: PropTypes.object,
    debug: PropTypes.bool,
};

export default CircleSpinner;
