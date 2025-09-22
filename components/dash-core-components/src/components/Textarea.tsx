/* eslint-disable no-unused-vars */
import React from 'react';
import {pick} from 'ramda';
import {PersistedProps, PersistenceTypes, TextAreaProps} from '../types';
import './css/textarea.css';

const textAreaProps = [
    'id',
    'form',
    'name',
    'placeholder',
    'wrap',
    'accessKey',
    'contextMenu',
    'dir',
    'draggable',
    'lang',
    'spellCheck',
    'style',
    'title',
] as const;

const asNumber = (value?: string | number): number | undefined => {
    return typeof value === 'string'
        ? isNaN(parseInt(value, 10))
            ? undefined
            : parseInt(value, 10)
        : value;
};
const asBool = (value?: string | boolean): boolean | undefined => {
    if (typeof value === 'string') {
        if (['true', 'TRUE', 'True'].includes(value)) {
            return true;
        }
        if (['false', 'FALSE', 'False'].includes(value)) {
            return false;
        }
        return undefined;
    }
    return value;
};

/**
 * A basic HTML textarea for entering multiline text.
 *
 */
const Textarea = ({
    setProps,
    n_blur = 0,
    n_blur_timestamp = -1,
    n_clicks = 0,
    n_clicks_timestamp = -1,
    ...props
}: TextAreaProps) => {
    const ctx = window.dash_component_api.useDashContext();
    const isLoading = ctx.useLoading();

    return (
        <textarea
            data-dash-is-loading={isLoading || undefined}
            className={'dash-textarea ' + props.className}
            value={props.value}
            cols={asNumber(props.cols)}
            rows={asNumber(props.rows)}
            disabled={asBool(props.disabled)}
            minLength={asNumber(props.minLength)}
            maxLength={asNumber(props.maxLength)}
            readOnly={asBool(props.readOnly)}
            required={asBool(props.required)}
            autoFocus={asBool(props.autoFocus)}
            contentEditable={asBool(props.contentEditable)}
            hidden={asBool(props.hidden)}
            tabIndex={asNumber(props.tabIndex)}
            onChange={e => {
                setProps({value: e.target.value});
            }}
            onBlur={() => {
                setProps({
                    n_blur: n_blur + 1,
                    n_blur_timestamp: Date.now(),
                });
            }}
            onClick={() => {
                setProps({
                    n_clicks: n_clicks + 1,
                    n_clicks_timestamp: Date.now(),
                });
            }}
            {...pick(textAreaProps, props)}
        />
    );
};

Textarea.dashPersistence = {
    persisted_props: [PersistedProps.value],
    persistence_type: PersistenceTypes.local,
};

export default Textarea;
