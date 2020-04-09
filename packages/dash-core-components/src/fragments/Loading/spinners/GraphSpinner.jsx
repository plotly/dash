import React from 'react';
import PropTypes from 'prop-types';

const GraphSpinner = ({status, fullscreen, debug, className, style}) => {
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
            <div>
                {debugTitle}
                <div className="dash-spinner dash-graph-spinner">
                    <div className="dash-graph-spinner__bottom">
                        <div className="dash-bar dash-bar__one" />
                        <div className="dash-bar dash-bar__two" />
                        <div className="dash-bar dash-bar__three" />
                    </div>
                    <div className="dash-graph-spinner__background">
                        <div className="dash-dot dash-dot__one" />
                        <div className="dash-dot dash-dot__two" />
                        <div className="dash-dot dash-dot__three" />
                        <div className="dash-dot dash-dot__four" />
                        <div className="dash-graph-spinner__bottom">
                            <div className="dash-vert dash-vert__one" />
                            <div className="dash-vert dash-vert__two" />
                            <div className="dash-vert dash-vert__three" />
                            <div className="dash-vert dash-vert__four" />
                        </div>
                    </div>
                </div>
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
                      .dash-graph-spinner {
                        display: flex;
                        margin: 0 auto;
                        width: 200px;
                        height: 128px;
                        position: relative;
                        z-index: -2;
                        border-radius: 4px;
                      }
                      .dash-graph-spinner__bottom {
                        display: flex;
                        margin-top: auto;
                        flex-direction: column;
                        height: 12px;
                        width: 100%;
                      }
                      .dash-graph-spinner__background {
                        width: 100%;
                        height: 100%;
                        display: block;
                        position: absolute;
                        z-index: -1;
                        display: flex;
                      }
                      .dash-bar {
                        height: 40px;
                        background-color: #119DFF;
                        animation: bar-one 2s infinite;
                        transform-origin: 0% 0%;
                        display: inline-flex;
                        border-radius: 8px;
                      }
                      .dash-bar__one {
                        transform: rotate(-45deg);
                        bottom: -10px;
                        left: 16px;
                        position: relative;
                      }
                      .dash-bar__two {
                        transform: rotate(25deg);
                        animation: bar-two 2s infinite;
                        left: 72px;
                        bottom: 48px;
                        position: relative;
                        animation-delay: 2s infinite;
                      }
                      .dash-bar__three {
                        transform: rotate(-30deg);
                        animation: bar-three 2s infinite;
                        left: 114px;
                        bottom: 27px;
                        position: relative;
                        animation-delay: 2s infinite;
                      }
                      .dash-vert {
                        display: inline-block;
                        transform-origin: 0% 0%;
                        position: absolute;
                        bottom: 0px;
                        width: 40px;
                      }
                      .dash-vert__one {
                        animation: vert-one 2s infinite;
                        background-color: #e763fa;
                      }
                      .dash-vert__two {
                        animation: vert-two 2s infinite;
                        left: 50px;
                        background-color: #636efa;
                      }
                      .dash-vert__three {
                        animation: vert-three 2s infinite;
                        left: 100px;
                        background-color: #00cc96;
                      }
                      .dash-vert__four {
                        animation: vert-four 2s infinite;
                        left: 150px;
                        background-color: #EF553B;
                      }
                      .dash-dot {
                        width: 10px;
                        height: 10px;
                        border-radius: 100%;
                        display: block;
                        background-color: #119DFF;
                        position: absolute;
                        z-index: 2;
                      }
                      .dash-dot__one {
                        bottom: 0px;
                        left: 16px;
                        animation: dot-one 2s infinite;
                      }
                      .dash-dot__two {
                        bottom: 48px;
                        left: 66px;
                        animation: dot-two 2s infinite;
                      }
                      .dash-dot__three {
                        bottom: 27px;
                        left: 114px;
                        animation: dot-three 2s infinite;
                      }
                      .dash-dot__four {
                        bottom: 56px;
                        left: 166px;
                        animation: dot-four 2s infinite;
                      }
                      @keyframes dot-one {
                        0%{
                          opacity: 0;
                        }
                        30% {
                          opacity: 1;
                        }
                        100% {
                          opacity: 1;
                        }
                      }
                      @keyframes dot-two {
                        0%{
                          opacity: 0;
                        }
                        30% {
                          opacity: 1;
                        }
                        60% {
                          opacity: 1;
                        }
                        100% {
                          opacity: 1;
                        }
                      }
                      @keyframes dot-three {
                        0%{
                          opacity: 0;
                        }
                        30% {
                          opacity: 0;
                        }
                        60% {
                          opacity: 1;
                        }
                        100% {
                          opacity: 1;
                        }
                      }
                      @keyframes dot-four {
                        0%{
                          opacity: 0;
                        }
                        30% {
                          opacity: 0;
                        }
                        60% {
                          opacity: 0;
                        }
                        100% {
                          opacity: 1;
                        }
                      }
                      @keyframes vert-one {
                        0% {
                          height: 0px;
                        }
                        100% {
                          height: 80px;
                        }
                      }
                      @keyframes vert-two {
                        0% {
                          height: 0px;
                        }
                        30% {
                          height: 0px;
                        }
                        100% {
                          height: 120px;
                        }
                      }
                      @keyframes vert-three {
                        0% {
                          height: 0px;
                        }
                        30% {
                          height: 0px;
                        }
                        50% {
                          height: 0px;
                        }
                        100% {
                          height: 100px;
                        }
                      }
                      @keyframes vert-four {
                        0% {
                          height: 0px;
                        }
                        30% {
                          height: 0px;
                        }
                        50% {
                          height: 0px;
                        }
                        60% {
                          height: 0px;
                        }
                        100% {
                          height: 60px;
                        }
                      }
                      @keyframes bar-one {
                        0% {
                          width: 0%;
                        }
                        30% {
                          width: 40%;
                        }
                        60% {
                          width: 40%;
                        }
                        100% {
                          width: 40%;
                        }
                      }
                      @keyframes bar-two {
                        0% {
                          width: 0%;
                        }
                        30% {
                          width: 0%;
                        }
                        60% {
                          width: 28%;
                        }
                        100% {
                          width: 28%;
                        }
                      }
                      @keyframes bar-three {
                        0% {
                          width: 0%;
                        }
                        30% {
                          width: 0%;
                        }
                        60% {
                          width: 0%;
                        }
                        100% {
                          width: 33%;
                        }
                      }
                      @keyframes dash-title {
                        0% {
                          opacity: 0.1;
                        }
                        50% {
                          opacity: 1;
                        }
                        100% {
                          opacity: 0.1;
                        }
                      }
                    `}
            </style>
        </div>
    );
};

GraphSpinner.propTypes = {
    status: PropTypes.object,
    color: PropTypes.string,
    className: PropTypes.string,
    fullscreen: PropTypes.bool,
    style: PropTypes.object,
    debug: PropTypes.bool,
};

export default GraphSpinner;
