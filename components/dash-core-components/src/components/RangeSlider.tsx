import {pick} from 'ramda';
import React, {lazy, Suspense} from 'react';
import {RangeSliderProps} from '../types';
import rangeSlider from '../utils/LazyLoader/rangeSlider';

import './css/sliders.css';

const RealRangeSlider = lazy(rangeSlider);

const defaultProps: Partial<RangeSliderProps> = {
    updatemode: 'mouseup',
    persisted_props: ['value'],
    persistence_type: 'local',
    verticalHeight: 400,
};

/**
 * A double slider with two handles.
 * Used for specifying a range of numerical values.
 */
export default function RangeSlider({
    updatemode = defaultProps.updatemode,
    persisted_props = defaultProps.persisted_props,
    persistence_type = defaultProps.persistence_type,
    verticalHeight = defaultProps.verticalHeight,
    ...rest
}: RangeSliderProps) {
    const props = {
        updatemode,
        persisted_props,
        persistence_type,
        verticalHeight,
        ...rest,
    };

    return (
        <Suspense fallback={null}>
            <RealRangeSlider {...props} />
        </Suspense>
    );
}

RangeSlider.dashPersistence = pick(
    ['persisted_props', 'persistence_type'],
    defaultProps
);
