import React from 'react';
import {TooltipProps} from '../types';
import './css/tooltip.css';

/**
 * A tooltip with an absolute position.
 */
const Tooltip = ({
    show = true,
    targetable = false,
    direction = 'right',
    border_color = 'var(--Dash-Stroke-Weak)',
    background_color = 'var(--Dash-Fill-Inverse-Strong)',
    className = '',
    zindex = 1,
    loading_text = 'Loading...',
    ...props
}: TooltipProps) => {
    const {bbox, id} = props;
    const show_tooltip = show && bbox;

    const ctx = window.dash_component_api.useDashContext();
    const is_loading = ctx.useLoading();

    const position = bbox ?? {x0: 0, x1: 0, y0: 0, y1: 0};

    const styles = {
        top: `${position?.y0}px`,
        left: `${position?.x0}px`,
        width: `${position?.x1 - position?.x0}px`,
        height: `${position?.y1 - position?.y0}px`,
        display: `${show_tooltip ? 'inline-block' : 'none'}`,
        pointerEvents: `${targetable ? 'auto' : 'none'}`,
        '--Dash-Tooltip-PointerEvents': targetable ? 'auto' : 'none',
        '--Dash-Tooltip-Border-Color': border_color,
        '--Dash-Tooltip-Background-Color': background_color,
        '--Dash-Tooltip-ZIndex': zindex,
    } as const;

    return (
        <>
            <div
                className="dcc-tooltip-bounding-box dash-tooltip"
                style={styles}
            >
                <div
                    className={`hover hover-${direction}`}
                    data-dash-is-loading={is_loading}
                >
                    <span
                        id={id}
                        className={`hover-content ${className}`}
                        style={props.style}
                    >
                        {is_loading ? (
                            <span>{loading_text}</span>
                        ) : (
                            props.children
                        )}
                    </span>
                </div>
            </div>
        </>
    );
};

export default Tooltip;
