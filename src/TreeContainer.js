'use strict';

import React, {Component} from 'react';
import PropTypes from 'prop-types';
import Registry from './registry';
import NotifyObservers from './components/core/NotifyObservers.react';
import {connect} from 'react-redux';
import {
    isNil,
    omit,
    contains,
    isEmpty,
    forEach,
    propOr,
    type,
    has,
} from 'ramda';
import {STATUS} from './constants/constants';

class TreeContainer extends Component {
    shouldComponentUpdate(nextProps) {
        return nextProps.layout !== this.props.layout;
    }

    render() {
        return recursivelyRender(this.props.layout, this.props.requestQueue);
    }
}

TreeContainer.propTypes = {
    layout: PropTypes.object,
    requestQueue: PropTypes.object,
};

function recursivelyRender(component, requestQueue) {
    if (contains(type(component), ['String', 'Number', 'Null', 'Boolean'])) {
        return component;
    }

    if (isEmpty(component)) {
        return null;
    }

    // Create list of child elements
    let children;

    const componentProps = propOr({}, 'props', component);

    if (
        !has('props', component) ||
        !has('children', component.props) ||
        typeof component.props.children === 'undefined'
    ) {
        // No children
        children = [];
    } else if (
        contains(type(component.props.children), [
            'String',
            'Number',
            'Null',
            'Boolean',
        ])
    ) {
        children = [component.props.children];
    } else {
        // One or multiple objects
        // Recursively render the tree
        // TODO - I think we should pass in `key` here.
        children = (Array.isArray(componentProps.children)
            ? componentProps.children
            : [componentProps.children]
        ).map(child => recursivelyRender(child, requestQueue));
    }

    if (!component.type) {
        /* eslint-disable no-console */
        console.error(type(component), component);
        /* eslint-enable no-console */
        throw new Error('component.type is undefined');
    }
    if (!component.namespace) {
        /* eslint-disable no-console */
        console.error(type(component), component);
        /* eslint-enable no-console */
        throw new Error('component.namespace is undefined');
    }
    const element = Registry.resolve(component.type, component.namespace);

    const parent = React.createElement(
        element,
        omit(['children'], component.props),
        ...children
    );

    // loading prop coming from TreeContainer
    let isLoading = false;
    let loadingProp;
    let loadingComponent;

    const id = componentProps.id;

    if (requestQueue && requestQueue.filter) {
        forEach(r => {
            const controllerId = isNil(r.controllerId) ? '' : r.controllerId;
            if (r.status === 'loading' && contains(id, controllerId)) {
                isLoading = true;
                [loadingComponent, loadingProp] = r.controllerId.split('.');
            }
        }, requestQueue);

        const thisRequest = requestQueue.filter(r => {
            const controllerId = isNil(r.controllerId) ? '' : r.controllerId;
            return contains(id, controllerId);
        });
        if (thisRequest.status === STATUS.OK) {
            isLoading = false;
        }
    }

    // Set loading state
    const loading_state = {
        is_loading: isLoading,
        prop_name: loadingProp,
        component_name: loadingComponent,
    };

    return (
        <NotifyObservers
            key={componentProps.id}
            id={componentProps.id}
            loading_state={loading_state}
        >
            {parent}
        </NotifyObservers>
    );
}

function mapStateToProps(state, ownProps) {
    return {
        layout: ownProps.layout,
        loading: ownProps.loading,
        requestQueue: state.requestQueue,
    };
}

export default connect(mapStateToProps)(TreeContainer);
