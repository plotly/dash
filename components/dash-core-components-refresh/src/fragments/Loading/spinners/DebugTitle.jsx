import React from 'react';

export default function DebugTitle({id, property}) {
    return (
        <h3 className="dash-loading-title">
            Loading #{id}
            's {property}
        </h3>
    )
} 
