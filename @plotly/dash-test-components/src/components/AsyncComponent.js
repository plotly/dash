import PropTypes from 'prop-types';
import React, { Suspense } from 'react';
import { asyncDecorator } from '@plotly/dash-component-plugins';
import asyncComponentLoader from './../fragments/AsyncComponentLoader';

const AsyncComponent = props => (<Suspense fallback={null}>
    <RealAsyncComponent {...props} />
</Suspense>);

const RealAsyncComponent = asyncDecorator(AsyncComponent, asyncComponentLoader);

AsyncComponent.propTypes = {
    id: PropTypes.string,
    value: PropTypes.string
};

AsyncComponent.defaultProps = {};

export default AsyncComponent;