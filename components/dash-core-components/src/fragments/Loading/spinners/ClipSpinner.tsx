import React from 'react';
import DebugTitle from './DebugTitle';
import {SpinnerProps} from '../types';

/**
 * Spinner created by David Hu, https://github.com/davidhu2000/react-spinners
 */
const ClipSpinner = ({
    status,
    color,
    fullscreen,
    debug,
    className,
    style,
}: SpinnerProps) => {
    let debugTitle;
    if (debug && status) {
        debugTitle = status.map((s, i) => <DebugTitle key={i} {...s} />);
    }
    let spinnerClass = fullscreen ? 'dash-spinner-container' : '';
    if (className) {
        spinnerClass += ` ${className}`;
    }
    return (
        <div style={style ? style : {}} className={spinnerClass}>
            {debugTitle}
            <div className="dash-spinner dash-clip-spinner" />
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
                    .dash-clip-spinner {
                        margin: 1rem auto;
                        width: 40px;
                        height: 40px;
                        box-sizing: border-box;
                        border: 2px solid ${color};
                        border-bottom-color: transparent;
                        border-radius: 100%;
                        animation: dash-clip-spinner-rotate 0.75s infinite linear both;
                    }

                    @keyframes dash-clip-spinner-rotate {
                        0% {
                            transform: rotate(0deg) scale(1);
                        }
                        50% {
                            transform: rotate(180deg) scale(0.8);
                        }
                        100% {
                            transform: rotate(360deg) scale(1);
                        }
                    }
                `}
            </style>
        </div>
    );
};

export default ClipSpinner;
