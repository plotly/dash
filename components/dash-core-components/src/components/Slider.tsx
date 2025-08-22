import {pick} from 'ramda';
import React, {lazy, Suspense} from 'react';
import {SliderProps} from '../types';
import slider from '../utils/LazyLoader/slider';

import './css/sliders.css';

const RealSlider = lazy(slider);

const defaultProps: Partial<SliderProps> = {
    updatemode: 'mouseup',
    persisted_props: ['value'],
    persistence_type: 'local',
    verticalHeight: 400,
};

/**
 * A slider component with a single handle.
 */
export default function Slider({
    updatemode = defaultProps.updatemode,
    persisted_props = defaultProps.persisted_props,
    persistence_type = defaultProps.persistence_type,
    verticalHeight = defaultProps.verticalHeight,
    ...rest
}: SliderProps) {
    const props = {
        updatemode,
        persisted_props,
        persistence_type,
        verticalHeight,
        ...rest,
    };

    return (
        <Suspense fallback={null}>
            <RealSlider {...props} />
        </Suspense>
    );
}

Slider.dashPersistence = pick(
    ['persisted_props', 'persistence_type'],
    defaultProps
);
