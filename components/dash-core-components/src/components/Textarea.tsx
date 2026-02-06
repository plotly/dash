/* eslint-disable no-unused-vars */
import React from 'react';
import {pick} from 'ramda';
import {PersistedProps, PersistenceTypes, TextAreaProps} from '../types';
import './css/textarea.css';

const textAreaProps = [
    'id',
    'cols',
    'rows',
    'minLength',
    'maxLength',
    'contentEditable',
    'tabIndex',
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
            disabled={!!props.disabled}
            readOnly={!!props.readOnly}
            required={!!props.required}
            autoFocus={!!props.autoFocus}
            hidden={!!props.hidden}
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
