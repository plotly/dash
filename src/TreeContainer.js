'use strict';

import React, {Component} from 'react';
import PropTypes from 'prop-types';
import Registry from './registry';
import {connect} from 'react-redux';
import {
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
import {STATUS} from './constants/constants';
import { notifyObservers, updateProps } from './actions';
import ComponentErrorBoundary from './components/error/ComponentErrorBoundary.react';

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

    getLoadingState(id, requestQueue) {
        // loading prop coming from TreeContainer
        let isLoading = false;
        let loadingProp;
        let loadingComponent;

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
        return {
            is_loading: isLoading,
            prop_name: loadingProp,
            component_name: loadingComponent,
        };
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
        return nextProps._dashprivate_layout !== this.props._dashprivate_layout;
    }

    getLayoutProps() {
        return propOr({}, 'props', this.props._dashprivate_layout);
    }

    render() {
        const {
            _dashprivate_dispatch,
            _dashprivate_layout,
            _dashprivate_requestQueue
        } = this.props;

        const layoutProps = this.getLayoutProps();

        const children = this.getChildren(layoutProps.children);
        const loadingState = this.getLoadingState(layoutProps.id, _dashprivate_requestQueue);
        const setProps = this.getSetProps(_dashprivate_dispatch);

        return (
            <ComponentErrorBoundary
                componentType={_dashprivate_layout.type}
                componentId={_dashprivate_layout.props.id}
            >
                {this.getComponent(_dashprivate_layout, children, loadingState, setProps)}
            </ComponentErrorBoundary>
        );
    }
}

TreeContainer.propTypes = {
    _dashprivate_dependencies: PropTypes.any,
    _dashprivate_dispatch: PropTypes.func,
    _dashprivate_layout: PropTypes.object,
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
        _dashprivate_loading: ownProps._dashprivate_loading,
        _dashprivate_paths: stateProps.paths,
        _dashprivate_requestQueue: stateProps.requestQueue,
    };
}

export const AugmentedTreeContainer = connect(mapStateToProps, mapDispatchToProps, mergeProps)(TreeContainer);

export default AugmentedTreeContainer;
