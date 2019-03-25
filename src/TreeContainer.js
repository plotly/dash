'use strict';

import React, {Component} from 'react';
import PropTypes from 'prop-types';
import Registry from './registry';
import {connect} from 'react-redux';
import {
    any,
    contains,
    filter,
    forEach,
    isEmpty,
    isNil,
    keysIn,
    map,
    mergeAll,
    omit,
    pick,
    propOr,
    type
} from 'ramda';
import { notifyObservers, updateProps } from './actions';

const SIMPLE_COMPONENT_TYPES = ['String', 'Number', 'Null', 'Boolean'];
const isSimpleComponent = component => contains(type(component), SIMPLE_COMPONENT_TYPES)

const createContainer = component => isSimpleComponent(component) ?
    component :
    (<AugmentedTreeContainer
        key={component && component.props && component.props.id}
        _dashprivate_layout={component}
    />);

class TreeContainer extends Component {
    getChildren(components) {
        if (!components) {
            return null;
        }

        return Array.isArray(components) ?
            map(createContainer, components) :
            createContainer(components);
    }

    getComponent(_dashprivate_layout, children, loading_state, setProps) {
        if (isEmpty(_dashprivate_layout)) {
            return null;
        }

        if (isSimpleComponent(_dashprivate_layout)) {
            return _dashprivate_layout;
        }

        if (!_dashprivate_layout.type) {
            /* eslint-disable no-console */
            console.error(type(_dashprivate_layout), _dashprivate_layout);
            /* eslint-enable no-console */
            throw new Error('component.type is undefined');
        }
        if (!_dashprivate_layout.namespace) {
            /* eslint-disable no-console */
            console.error(type(_dashprivate_layout), _dashprivate_layout);
            /* eslint-enable no-console */
            throw new Error('component.namespace is undefined');
        }
        const element = Registry.resolve(_dashprivate_layout.type, _dashprivate_layout.namespace);

        return React.createElement(
            element,
            mergeAll([
                omit(['children'], _dashprivate_layout.props),
                { loading_state, setProps }
            ]),
            ...(Array.isArray(children) ? children : [children])
        );
    }

    getSetProps() {
        return newProps => {
            const {
                _dashprivate_dependencies,
                _dashprivate_dispatch,
                _dashprivate_paths
            } = this.props;

            const id = this.getLayoutProps().id;

            // Identify the modified props that are required for callbacks
            const watchedKeys = filter(key =>
                _dashprivate_dependencies &&
                _dashprivate_dependencies.find(dependency =>
                    dependency.inputs.find(input => input.id === id && input.property === key) ||
                    dependency.state.find(state => state.id === id && state.property === key)
                )
            )(keysIn(newProps));

            // Always update this component's props
            _dashprivate_dispatch(updateProps({
                props: newProps,
                id: id,
                itempath: _dashprivate_paths[id]
            }));

            // Only dispatch changes to Dash if a watched prop changed
            if (watchedKeys.length) {
                _dashprivate_dispatch(notifyObservers({
                    id: id,
                    props: pick(watchedKeys)(newProps)
                }));
            }

        };
    }

    shouldComponentUpdate(nextProps) {
        const { _dashprivate_layout, _dashprivate_loadingState } = nextProps;

        return _dashprivate_layout !== this.props._dashprivate_layout ||
            _dashprivate_loadingState.is_loading !== this.props._dashprivate_loadingState.is_loading;
    }

    getLayoutProps() {
        return propOr({}, 'props', this.props._dashprivate_layout);
    }

    render() {
        const {
            _dashprivate_dispatch,
            _dashprivate_layout,
            _dashprivate_loadingState
        } = this.props;

        const layoutProps = this.getLayoutProps();

        const children = this.getChildren(layoutProps.children);
        const setProps = this.getSetProps(_dashprivate_dispatch);

        return this.getComponent(_dashprivate_layout, children, _dashprivate_loadingState, setProps);
    }
}

TreeContainer.propTypes = {
    _dashprivate_dependencies: PropTypes.any,
    _dashprivate_dispatch: PropTypes.func,
    _dashprivate_layout: PropTypes.object,
    _dashprivate_loadingState: PropTypes.object,
    _dashprivate_paths: PropTypes.any,
    _dashprivate_requestQueue: PropTypes.object,
};

function mapDispatchToProps(dispatch) {
    return { dispatch };
}

function mapStateToProps(state) {
    return {
        dependencies: state.dependenciesRequest.content,
        paths: state.paths,
        requestQueue: state.requestQueue
    };
}

function mergeProps(stateProps, dispatchProps, ownProps) {
    return {
        _dashprivate_dependencies: stateProps.dependencies,
        _dashprivate_dispatch: dispatchProps.dispatch,
        _dashprivate_layout: ownProps._dashprivate_layout,
        _dashprivate_loadingState: getLoadingState(ownProps._dashprivate_layout, stateProps.requestQueue),
        _dashprivate_paths: stateProps.paths,
        _dashprivate_requestQueue: stateProps.requestQueue,
    };
}

function getLoadingState(layout, requestQueue) {
    const ids = isLoadingComponent(layout) ?
        getNestedIds(layout) :
        (layout && layout.props.id ?
            [layout.props.id] :
            []);

    let isLoading = false;
    let loadingProp;
    let loadingComponent;

    if (requestQueue) {
        forEach(r => {
            const controllerId = isNil(r.controllerId) ? '' : r.controllerId;
            if (r.status === 'loading' && any(id => contains(id, controllerId), ids)) {
                isLoading = true;
                [loadingComponent, loadingProp] = r.controllerId.split('.');
            }
        }, requestQueue);
    }

    // Set loading state
    return {
        is_loading: isLoading,
        prop_name: loadingProp,
        component_name: loadingComponent,
    };
}

function getNestedIds(layout) {
    const ids = [];
    const queue = [layout];

    while (queue.length) {
        const elementLayout = queue.shift();

        const props = elementLayout &&
            elementLayout.props;

        if (!props) {
            continue;
        }

        const { children, id } = props;

        if (id) {
            ids.push(id);
        }

        if (children) {
            const filteredChildren = filter(
                child => !isSimpleComponent(child) && !isLoadingComponent(child),
                Array.isArray(children) ? children : [children]
            );

            queue.push(...filteredChildren);
        }
    }

    return ids;
}

function isLoadingComponent(layout) {
    return Registry.resolve(layout.type, layout.namespace)._dashprivate_isLoadingComponent;
}

export const AugmentedTreeContainer = connect(mapStateToProps, mapDispatchToProps, mergeProps)(TreeContainer);

export default AugmentedTreeContainer;
