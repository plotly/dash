import React from 'react';

import _JSXStyle from 'styled-jsx/style';
import {TooltipProps} from '../../types';

/**
 * A tooltip with an absolute position.
 */
const Tooltip = ({
    show = true,
    targetable = false,
    direction = 'right',
    border_color = '#d6d6d6',
    background_color = 'white',
    className = '',
    zindex = 1,
    loading_text = 'Loading...',
    ...props
}: TooltipProps) => {
    const {bbox, id} = props;
    const show_tooltip = show && bbox;

    const ctx = window.dash_component_api.useDashContext();
    const is_loading = ctx.useLoading();

    return (
        <>
            <div className="dcc-tooltip-bounding-box">
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
            <style jsx>{`
                .dcc-tooltip-bounding-box {
                    position: absolute;
                    top: ${bbox?.y0 || 0}px;
                    left: ${bbox?.x0 || 0}px;
                    width: ${bbox?.x1 - bbox?.x0 || 0}px;
                    height: ${bbox?.y1 - bbox?.y0 || 0}px;
                    display: ${show_tooltip ? 'inline-block' : 'none'};
                    pointer-events: ${targetable ? 'auto' : 'none'};
                }
                .hover {
                    position: absolute;
                }
                .hover-right {
                    /* Offset so that the triangle caret lands directly on what's hovered */
                    transform: translate(5px, 0);
                    top: 50%;
                    left: 100%;
                }
                .hover-left {
                    transform: translate(-5px, 0);
                    top: 50%;
                }
                .hover-bottom {
                    transform: translate(0, 6px);
                    top: 100%;
                    left: 50%;
                }
                .hover-top {
                    transform: translate(0, -5px);
                    left: 50%;
                }
                .hover-content {
                    position: absolute;
                    border: 1px solid ${border_color};
                    border-radius: 2px;
                    padding: 5px 10px;
                    background: ${background_color};
                    white-space: nowrap;
                    z-index: ${zindex};
                    pointer-events: none;
                }
                .hover .hover-content,
                .hover-right .hover-content {
                    transform: translate(0, -50%);
                }
                .hover-left .hover-content {
                    transform: translate(-100%, -50%);
                }
                .hover-top .hover-content {
                    transform: translate(-50%, -100%);
                }
                .hover-bottom .hover-content {
                    transform: translate(-50%, 0);
                }
                /* Add a small triangle on the left side of the box */
                .hover:before,
                .hover:after {
                    content: '';
                    width: 0;
                    height: 0;
                    position: absolute;
                    border-style: solid;
                    top: -6px;
                    z-index: ${zindex};
                }
                .hover:before,
                .hover:after,
                .hover-right:before,
                .hover-right:after {
                    border-width: 6px 6px 6px 0;
                }
                .hover-top:before,
                .hover-top:after {
                    border-width: 6px 6px 0 6px;
                }
                .hover-bottom:before,
                .hover-bottom:after {
                    border-width: 0 6px 6px 6px;
                }
                .hover-left:before,
                .hover-left:after {
                    border-width: 6px 0 6px 6px;
                }
                .hover:before,
                .hover-right:before {
                    border-color: transparent ${border_color} transparent
                        transparent;
                    left: -5px;
                }
                .hover:after,
                .hover-right:after {
                    border-color: transparent ${background_color} transparent
                        transparent;
                    left: -4px;
                }
                .hover-left:before {
                    border-color: transparent transparent transparent
                        ${border_color};
                    left: -1px;
                }
                .hover-left:after {
                    border-color: transparent transparent transparent
                        ${background_color};
                    left: -2px;
                }
                .hover-top:before,
                .hover-top:after,
                .hover-bottom:before,
                .hover-bottom:after {
                    left: -6px;
                }
                .hover-bottom:before {
                    border-color: transparent transparent ${border_color}
                        transparent;
                }
                .hover-bottom:after {
                    border-color: transparent transparent ${background_color}
                        transparent;
                    top: -5px;
                }
                .hover-top:before {
                    border-color: ${border_color} transparent transparent
                        transparent;
                    top: -1px;
                }
                .hover-top:after {
                    border-color: ${background_color} transparent transparent
                        transparent;
                    top: -2px;
                }
            `}</style>
        </>
    );
};

export default Tooltip;
