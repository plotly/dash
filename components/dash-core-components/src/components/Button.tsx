import React from 'react';
import {ButtonProps} from '../types';
import './css/button.css';

/**
 * Similar to dash.html.Button, but with theming and styles applied.
 */
const Button = ({
    setProps,
    n_blur = 0,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    n_blur_timestamp = -1,
    n_clicks = 0,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    n_clicks_timestamp = -1,
    type = 'button',
    className,
    children,
    ...props
}: ButtonProps) => {
    const ctx = window.dash_component_api.useDashContext();
    const isLoading = ctx.useLoading();

    return (
        <button
            data-dash-is-loading={isLoading || undefined}
            className={'dash-button ' + (className ?? '')}
            onBlur={() => {
                setProps({
                    n_blur: n_blur + 1,
                    n_blur_timestamp: Date.now(),
                });
            }}
            onClick={() => {
                setProps({
                    n_clicks: n_clicks + 1,
                    n_clicks_timestamp: Date.now(),
                });
            }}
            type={type}
            {...props}
        >
            {children}
        </button>
    );
};

export default Button;
