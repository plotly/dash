import React, {lazy, Suspense} from 'react';
import {PersistedProps, PersistenceTypes, RangeSliderProps} from '../types';
import rangeSlider from '../utils/LazyLoader/rangeSlider';

import './css/sliders.css';

const RealRangeSlider = lazy(rangeSlider);

/**
 * A double slider with two handles.
 * Used for specifying a range of numerical values.
 */
export default function RangeSlider({
    updatemode = 'mouseup',
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persisted_props = [PersistedProps.value],
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persistence_type = PersistenceTypes.local,
    // eslint-disable-next-line no-magic-numbers
    verticalHeight = 400,
    step = undefined,
    ...props
}: RangeSliderProps) {
    // Some considerations for the default value of `step`:
    // If the range consists of integers, default to a value of `1`
    // Otherwise, leave it undefined
    if (
        typeof step === 'undefined' &&
        Number.isInteger(props.min) &&
        Number.isInteger(props.max)
    ) {
        step = 1;
    }

    return (
        <Suspense fallback={null}>
            <RealRangeSlider
                updatemode={updatemode}
                verticalHeight={verticalHeight}
                step={step}
                {...props}
            />
        </Suspense>
    );
}

RangeSlider.dashPersistence = {
    persisted_props: [PersistedProps.value],
    persistence_type: PersistenceTypes.local,
};
