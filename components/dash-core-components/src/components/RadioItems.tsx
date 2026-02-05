import React, {useMemo} from 'react';
import {RadioItemsProps, PersistedProps, PersistenceTypes} from '../types';
import './css/radioitems.css';

import {sanitizeOptions} from '../utils/optionTypes';
import LoadingElement from '../utils/_LoadingElement';
import {OptionsList} from '../utils/optionRendering';
import {isNil} from 'ramda';

/**
 * RadioItems is a component that encapsulates several radio item inputs.
 * The values and labels of the RadioItems is specified in the `options`
 * property and the seleced item is specified with the `value` property.
 * Each radio item is rendered as an input with a surrounding label.
 */
export default function RadioItems({
    className,
    id,
    style,
    setProps,
    value,
    inputStyle = {},
    inputClassName = '',
    labelStyle = {},
    labelClassName = '',
    options = [],
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persisted_props = [PersistedProps.value],
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persistence_type = PersistenceTypes.local,
    inline = false,
}: RadioItemsProps) {
    const sanitizedOptions = useMemo(() => {
        return sanitizeOptions(options);
    }, [options]);

    const stylingProps = {
        id,
        className: 'dash-radioitems ' + (className ?? ''),
        style,
        optionClassName: inline ? 'dash-radioitems-inline' : undefined,
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
                    inputType="radio"
                    options={sanitizedOptions}
                    selected={isNil(value) ? [] : [value]}
                    onSelectionChange={selection => {
                        if (selection.length) {
                            setProps({value: selection[selection.length - 1]});
                        }
                    }}
                    {...stylingProps}
                />
            )}
        </LoadingElement>
    );
}

RadioItems.dashPersistence = {
    persisted_props: [PersistedProps.value],
    persistence_type: PersistenceTypes.local,
};
