import React from 'react';
import {
    formatSliderTooltip,
    transformSliderTooltip,
} from '../utils/formatSliderTooltip';
import {SliderTooltip} from '../types';

type TooltipProps = {
    id?: string;
    index: number;
    value: number;
    tooltip: SliderTooltip;
};

export const Tooltip = ({tooltip, value, index: key, id}: TooltipProps) => {
    const formatTooltipContent = (value: number, index: number) => {
        let displayValue: string | number = value;
        if (tooltip?.transform) {
            displayValue = transformSliderTooltip(tooltip.transform, value);
        }
        return (
            <div
                id={`${id}-tooltip-${index + 1}-content`}
                style={tooltip?.style}
            >
                {formatSliderTooltip(
                    tooltip?.template || '{value}',
                    displayValue
                )}
            </div>
        );
    };

    const classNames = [
        'dash-slider-tooltip',
        tooltip.always_visible ? 'always-visible' : '',
    ];

    const placement = (tooltip.placement ?? 'top').toLowerCase();
    const position: React.CSSProperties = {transform: ''};

    if (placement.includes('top')) {
        position.bottom = 'calc(100% + var(--Dash-Spacing))';
    } else if (placement.includes('bottom')) {
        position.top = 'calc(100% + var(--Dash-Spacing))';
    } else {
        position.top = '50%';
        position.transform += 'translateY(-50%)';
    }

    if (placement.includes('left')) {
        position.right = 'calc(100% + var(--Dash-Spacing))';
    } else if (placement.includes('right')) {
        position.left = 'calc(100% + var(--Dash-Spacing))';
    } else {
        position.left = '50%';
        position.transform += 'translateX(-50%)';
    }

    return (
        <div className={classNames.join(' ')} style={position}>
            {formatTooltipContent(value, key)}
        </div>
    );
};
