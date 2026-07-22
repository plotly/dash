import React from 'react';

interface LoadingElementProps {
    children: (props: Record<string, unknown>) => React.ReactElement;
}

/**
 * The loading element is used to add `data-dash-is-loading` attribute
 * on html elements. This is used to customize CSS when a component is
 * loading.
 *
 * See: https://dash.plotly.com/loading-states#check-loading-states-from-components
 */
function LoadingElement({children}: LoadingElementProps) {
    const ctx = window.dash_component_api.useDashContext();
    const loading = ctx.useLoading();

    const additionalProps: Record<string, unknown> = {};
    if (loading) {
        additionalProps['data-dash-is-loading'] = true;
    }

    return children(additionalProps);
}

export default LoadingElement;
