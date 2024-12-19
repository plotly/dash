import React from 'react';
import PropTypes from 'prop-types';

export default function LoadingDiv({children, ...props}) {
    const ctx = window.dash_component_api.useDashContext();
    const loading = ctx.useLoading();
    return (
        <div {...props} data-dash-is-loading={loading || undefined}>
            {children}
        </div>
    );
}

LoadingDiv.propTypes = {
    children: PropTypes.node,
};
