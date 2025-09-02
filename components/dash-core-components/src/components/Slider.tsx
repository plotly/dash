import React, {lazy, Suspense} from 'react';
import {SliderProps} from '../types';
import slider from '../utils/LazyLoader/slider';

import './css/sliders.css';

const RealSlider = lazy(slider);

enum PersistenceTypes {
    'local' = 'local',
    'session' = 'session',
    'memory' = 'memory',
}

enum PersistedProps {
    'value' = 'value',
}

/**
 * A slider component with a single handle.
 */
export default function Slider({
    updatemode = 'mouseup',
    persisted_props = [PersistedProps.value],
    persistence_type = PersistenceTypes.local,
    // eslint-disable-next-line no-magic-numbers
    verticalHeight = 400,
    step = 1,
    ...rest
}: SliderProps) {
    const props = {
        updatemode,
        persisted_props,
        persistence_type,
        verticalHeight,
        step,
        ...rest,
    };

    return (
        <Suspense fallback={null}>
            <RealSlider {...props} />
        </Suspense>
    );
}

Slider.dashPersistence = {
    persisted_props: [PersistedProps.value],
    persistence_type: PersistenceTypes.local,
};
