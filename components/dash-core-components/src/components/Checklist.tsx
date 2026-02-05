import React, {useMemo} from 'react';
import {ChecklistProps, PersistedProps, PersistenceTypes} from '../types';
import './css/checklist.css';

import {sanitizeOptions} from '../utils/optionTypes';
import LoadingElement from '../utils/_LoadingElement';
import {OptionsList} from '../utils/optionRendering';

/**
 * Checklist is a component that encapsulates several checkboxes.
 * The values and labels of the checklist are specified in the `options`
 * property and the checked items are specified with the `value` property.
 * Each checkbox is rendered as an input with a surrounding label.
 */
export default function Checklist({
    className,
    id,
    style,
    setProps,
    inputStyle = {},
    inputClassName = '',
    labelStyle = {},
    labelClassName = '',
    options = [],
    value = [],
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persisted_props = [PersistedProps.value],
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persistence_type = PersistenceTypes.local,
    inline = false,
}: ChecklistProps) {
    const sanitizedOptions = useMemo(() => {
        return sanitizeOptions(options);
    }, [options]);

    const stylingProps = {
        id,
        className: 'dash-checklist ' + (className ?? ''),
        style,
        optionClassName: inline ? 'dash-checklist-inline' : undefined,
        inputStyle,
        inputClassName,
        labelStyle,
        labelClassName,
    };

    return (
        <LoadingElement>
            {loadingProps => (
                <OptionsList
                    {...loadingProps}
                    options={sanitizedOptions}
                    selected={value ?? []}
                    onSelectionChange={selection => {
                        setProps({value: selection});
                    }}
                    {...stylingProps}
                />
            )}
        </LoadingElement>
    );
}

Checklist.dashPersistence = {
    persisted_props: [PersistedProps.value],
    persistence_type: PersistenceTypes.local,
};
