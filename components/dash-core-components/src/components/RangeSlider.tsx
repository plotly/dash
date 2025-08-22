import React, {lazy, Suspense} from 'react';
import {RangeSliderProps} from '../types';
import rangeSlider from '../utils/LazyLoader/rangeSlider';

import './css/sliders.css';

const RealRangeSlider = lazy(rangeSlider);

enum PersistenceTypes {
    'local' = 'local',
    'session' = 'session',
    'memory' = 'memory',
}

enum PersistedProps {
    'value' = 'value',
}

/**
 * A double slider with two handles.
 * Used for specifying a range of numerical values.
 */
export default function RangeSlider({
    updatemode = 'mouseup',
    persisted_props = [PersistedProps.value],
    persistence_type = PersistenceTypes.local,
    // eslint-disable-next-line no-magic-numbers
    verticalHeight = 400,
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

RangeSlider.dashPersistence = {
    persisted_props: [PersistedProps.value],
    persistence_type: PersistenceTypes.local,
};
