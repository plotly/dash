import React from 'react';
import PropTypes from 'prop-types';

/**
 * The loading element is used to add `data-dash-is-loading` attribute
 * on html elements. This is used to customize CSS when a component is
 * loading.
 *
 * See: https://dash.plotly.com/loading-states#check-loading-states-from-components
 */
export default function LoadingElement({elementType = 'div', ...props}) {
    const ctx = window.dash_component_api.useDashContext();
    const loading = ctx.useLoading();

    const givenProps = {
        ...props,
    };
    if (loading) {
        givenProps['data-dash-is-loading'] = true;
    }

    return React.createElement(elementType, givenProps);
}

LoadingElement.propTypes = {
    children: PropTypes.node,
    elementType: PropTypes.string,
};
