import React, {lazy, Suspense} from 'react';
import {PersistedProps, PersistenceTypes, SliderProps} from '../types';
import slider from '../utils/LazyLoader/slider';
import './css/sliders.css';

const RealSlider = lazy(slider);

/**
 * A slider component with a single handle.
 */
export default function Slider({
    updatemode = 'mouseup',
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persisted_props = [PersistedProps.value],
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persistence_type = PersistenceTypes.local,
    // eslint-disable-next-line no-magic-numbers
    verticalHeight = 400,
    step = 1,
    ...props
}: SliderProps) {
    return (
        <Suspense fallback={null}>
            <RealSlider
                updatemode={updatemode}
                verticalHeight={verticalHeight}
                step={step}
                {...props}
            />
        </Suspense>
    );
}

Slider.dashPersistence = {
    persisted_props: [PersistedProps.value],
    persistence_type: PersistenceTypes.local,
};
