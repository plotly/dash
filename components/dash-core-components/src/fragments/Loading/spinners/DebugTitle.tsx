import React from 'react';
import {DebugTitleProps} from '../types';

export default function DebugTitle({id, property}: DebugTitleProps) {
    return (
        <h3 className="dash-loading-title">
            Loading #{id}
            &apos;s {property}
        </h3>
    );
}
