import React, {lazy, Suspense} from 'react';
import {PersistedProps, PersistenceTypes, DateRangeSliderProps} from '../types';
import dateRangeSlider from '../utils/LazyLoader/dateRangeSlider';

import './css/sliders.css';

const RealDateRangeSlider = lazy(dateRangeSlider);

/**
 * A date range slider component.
 * Used for specifying a range of dates with optional disabled date indicators
 * and calendar-aware stepping.
 */
export default function DateRangeSlider({
    updatemode = 'mouseup',
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persisted_props = [PersistedProps.value],
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persistence_type = PersistenceTypes.local,
    // eslint-disable-next-line no-magic-numbers
    verticalHeight = 400,
    allow_direct_input = true,
    disabled_dates_indicator = true,
    ...props
}: DateRangeSliderProps) {
    return (
        <Suspense fallback={null}>
            <RealDateRangeSlider
                updatemode={updatemode}
                verticalHeight={verticalHeight}
                allow_direct_input={allow_direct_input}
                disabled_dates_indicator={disabled_dates_indicator}
                {...props}
            />
        </Suspense>
    );
}

DateRangeSlider.dashPersistence = {
    persisted_props: [PersistedProps.value],
    persistence_type: PersistenceTypes.local,
};
