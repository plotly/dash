import React, {useEffect, useRef, useState} from 'react';
import PropTypes from 'prop-types';

import _JSXStyle from 'styled-jsx/style'; // eslint-disable-line no-unused-vars

/**
 * A tooltip with an absolute position.
 */
const Tooltip = props => {
    const {
        bbox,
        border_color,
        background_color,
        id,
        loading_state,
        auto_direction_container: autoDirectionContainer,
    } = props;
    const is_loading = loading_state?.is_loading;
    const show = props.show && bbox;
    const tooltipElement = useRef();

    const initialDirection =
        props.direction === 'auto' ? 'right' : props.direction;
    const [realDirection, setRealDirection] = useState(initialDirection);

    const getRealHiddenPart = value => {
        return value > 0 ? value : 0;
    };

    const calculateHiddenPart = (parentRect, tooltipRect) => {
        const hiddenDirections = [
            {
                direction: 'left',
                value: getRealHiddenPart(parentRect.left - tooltipRect.left),
            },
            {
                direction: 'right',
                value: getRealHiddenPart(tooltipRect.right - parentRect.right),
            },
            {
                direction: 'top',
                value: getRealHiddenPart(parentRect.top - tooltipRect.top),
            },
            {
                direction: 'bottom',
                value: getRealHiddenPart(
                    tooltipRect.bottom - parentRect.bottom
                ),
            },
        ];

        return hiddenDirections.reduce((sum, hidden) => sum + hidden.value, 0);
    };

    const setAutoDirection = () => {
        if (!tooltipElement.current || props.direction !== 'auto' || !show) {
            return;
        }

        let tooltipRect = tooltipElement.current?.getBoundingClientRect();
        const parent = autoDirectionContainer
            ? document.querySelector(autoDirectionContainer)
            : tooltipElement.current?.parentElement.parentElement.parentElement;

        if (!parent) {
            return;
        }

        const parentRect = parent?.getBoundingClientRect();

        const bboxCenter = {
            x: (bbox.x0 + bbox.x1) / 2,
            y: (bbox.y0 + bbox.y1) / 2,
        };

        const tooltipCenter = {
            x: (tooltipRect.left + tooltipRect.right) / 2,
            y: (tooltipRect.top + tooltipRect.bottom) / 2,
        };

        const xDelta = tooltipCenter.x - bboxCenter.x;
        const yDelta = tooltipCenter.y - bboxCenter.y;

        tooltipRect = {
            left: tooltipRect.left - xDelta,
            right: tooltipRect.right - xDelta,
            top: tooltipRect.top - yDelta,
            bottom: tooltipRect.bottom - yDelta,
            width: tooltipRect.width,
            height: tooltipRect.height,
        };

        const rightDirectionTooltipRect = {
            ...tooltipRect,
            left: tooltipRect.left + tooltipRect.width / 2,
            right: tooltipRect.right + tooltipRect.width / 2,
        };

        const leftDirectionTooltipRect = {
            ...tooltipRect,
            left: tooltipRect.left - tooltipRect.width / 2,
            right: tooltipRect.right - tooltipRect.width / 2,
        };

        const topDirectionTooltipRect = {
            ...tooltipRect,
            top: tooltipRect.top - tooltipRect.height / 2,
            bottom: tooltipRect.bottom - tooltipRect.height / 2,
        };

        const bottomDirectionTooltipRect = {
            ...tooltipRect,
            top: tooltipRect.top + tooltipRect.height / 2,
            bottom: tooltipRect.bottom + tooltipRect.height / 2,
        };

        let directionsHiddenParts = [
            {
                direction: 'right',
                value: calculateHiddenPart(
                    parentRect,
                    rightDirectionTooltipRect
                ),
            },
            {
                direction: 'left',
                value: calculateHiddenPart(
                    parentRect,
                    leftDirectionTooltipRect
                ),
            },
            {
                direction: 'top',
                value: calculateHiddenPart(parentRect, topDirectionTooltipRect),
            },
            {
                direction: 'bottom',
                value: calculateHiddenPart(
                    parentRect,
                    bottomDirectionTooltipRect
                ),
            },
        ];

        directionsHiddenParts = directionsHiddenParts.sort(
            (a, b) => a.value - b.value
        );

        setRealDirection(directionsHiddenParts[0].direction);
    };

    useEffect(setAutoDirection, [
        show,
        props.direction,
        bbox,
        props.children,
        autoDirectionContainer,
    ]);

    return (
        <>
            <div className="dcc-tooltip-bounding-box">
                <span
                    data-dash-is-loading={is_loading || undefined}
                    className={`hover hover-${realDirection}`}
                >
                    <span
                        id={id}
                        className={`hover-content ${props.className}`}
                        ref={tooltipElement}
                        style={props.style}
                    >
                        {is_loading ? (
                            <span>{props.loading_text}</span>
                        ) : (
                            props.children
                        )}
                    </span>
                </span>
            </div>
            <style jsx>{`
                .dcc-tooltip-bounding-box {
                    position: absolute;
                    top: ${bbox?.y0 || 0}px;
                    left: ${bbox?.x0 || 0}px;
                    width: ${bbox?.x1 - bbox?.x0 || 0}px;
                    height: ${bbox?.y1 - bbox?.y0 || 0}px;
                    display: ${show ? 'inline-block' : 'none'};
                    pointer-events: ${props.targetable ? 'auto' : 'none'};
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
                    z-index: ${props.zindex};
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
                    z-index: ${props.zindex};
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

Tooltip.defaultProps = {
    show: true,
    targetable: false,
    direction: 'right',
    border_color: '#d6d6d6',
    background_color: 'white',
    className: '',
    zindex: 1,
    loading_text: 'Loading...',
};

Tooltip.propTypes = {
    /**
     * The contents of the tooltip
     */
    children: PropTypes.node,

    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string,

    /**
     * The class of the tooltip
     */
    className: PropTypes.string,

    /**
     * The style of the tooltip
     */
    style: PropTypes.object,

    /**
     * The bounding box coordinates of the item to label, in px relative to
     * the positioning parent of the Tooltip component.
     */
    bbox: PropTypes.exact({
        x0: PropTypes.number,
        y0: PropTypes.number,
        x1: PropTypes.number,
        y1: PropTypes.number,
    }),

    /**
     * Whether to show the tooltip
     */
    show: PropTypes.bool,

    /**
     * The side of the `bbox` on which the tooltip should open.
     */
    direction: PropTypes.oneOf(['top', 'right', 'bottom', 'left', 'auto']),

    /**
     * Query selector for container in which tooltip should be visible.
     * If not set the tooltip`s parent element will be used.
     */
    auto_direction_container: PropTypes.string,

    /**
     * Color of the tooltip border, as a CSS color string.
     */
    border_color: PropTypes.string,

    /**
     * Color of the tooltip background, as a CSS color string.
     */
    background_color: PropTypes.string,

    /**
     * The text displayed in the tooltip while loading
     */
    loading_text: PropTypes.string,

    /**
     * The `z-index` CSS property to assign to the tooltip. Components with
     * higher values will be displayed on top of components with lower values.
     */
    zindex: PropTypes.number,

    /**
     * Whether the tooltip itself can be targeted by pointer events.
     * For tooltips triggered by hover events, typically this should be left
     * `false` to avoid the tooltip interfering with those same events.
     */
    targetable: PropTypes.bool,

    /**
     * Dash-assigned callback that gets fired when the value changes.
     */
    setProps: PropTypes.func,

    /**
     * Object that holds the loading state object coming from dash-renderer
     */
    loading_state: PropTypes.shape({
        /**
         * Determines if the component is loading or not
         */
        is_loading: PropTypes.bool,
        /**
         * Holds which property is loading
         */
        prop_name: PropTypes.string,
        /**
         * Holds the name of the component that is loading
         */
        component_name: PropTypes.string,
    }),
};

export default Tooltip;
