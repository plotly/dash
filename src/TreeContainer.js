import React, {Component} from 'react';
import PropTypes from 'prop-types';
import Registry from './registry';
import {connect} from 'react-redux';
import {assertPropTypes} from 'check-prop-types';
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
import ComponentErrorBoundary from './components/error/ComponentErrorBoundary.react';
<<<<<<< HEAD
// import ComponentErrorBoundary from './components/error/SimpleErrorBoundary.react';
=======
import { assertPropTypes } from 'check-prop-types';
>>>>>>> dev-tools-props

const SIMPLE_COMPONENT_TYPES = ['String', 'Number', 'Null', 'Boolean'];
const isSimpleComponent = component => contains(type(component), SIMPLE_COMPONENT_TYPES)

const createContainer = component => isSimpleComponent(component) ?
    component :
    (<AugmentedTreeContainer
        key={component && component.props && component.props.id}
        _dashprivate_layout={component}
    />);

function CheckedComponent(p) {
    const { element, layout, props, children } = p;

    assertPropTypes(
        element.propTypes,
        layout,
        'component prop', element);

    return React.createElement(
        element,
        mergeAll([layout, props]),
        ...(Array.isArray(children) ? children : [children])
    );
}

CheckedComponent.propTypes = {
    children: PropTypes.any,
    element: PropTypes.any,
    layout: PropTypes.any,
    props: PropTypes.any
};
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
<<<<<<< HEAD
        const component = Registry.resolve(_dashprivate_layout.type, _dashprivate_layout.namespace);

        const getCheckedElement = (component) => {
            return class CheckedComponent extends React.Component {
                componentDidMount() {
                    assertPropTypes(
                        component.propTypes,
                        _dashprivate_layout.props,
                        'component prop', component
                    );
                }
                render() {
                    return React.createElement(
                        component,
                        mergeAll([
                            omit(['children'], _dashprivate_layout.props),
                            { loading_state, setProps }
                        ]),
                        children
                    );
                }
            }
        };

        if (Array.isArray(children)) {
            return React.createElement(
                component,
                mergeAll([
                    omit(['children'], _dashprivate_layout.props),
                    { loading_state, setProps }
                ]),
                ...children
            );
        }
        const checkedElement = React.createElement(getCheckedElement(component));
        return (
            <ComponentErrorBoundary
                componentType={_dashprivate_layout.type}
                componentId={_dashprivate_layout.props.id}
            >
                {checkedElement}
            </ComponentErrorBoundary>
        );
=======
        const element = Registry.resolve(_dashprivate_layout.type, _dashprivate_layout.namespace);

        const layout = omit(['children'], _dashprivate_layout.props);

        return (<ComponentErrorBoundary
            componentType={_dashprivate_layout.type}
            componentId={_dashprivate_layout.props.id}
            key={element && element.props && element.props.id}
        >
            <CheckedComponent
                children={children}
                element={element}
                layout={layout}
                props={{ loading_state, setProps }}
            />
        </ComponentErrorBoundary>);
>>>>>>> dev-tools-props
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
<<<<<<< HEAD
    };
=======
    }
>>>>>>> dev-tools-props
}

TreeContainer.propTypes = {
    _dashprivate_dependencies: PropTypes.any,
    _dashprivate_dispatch: PropTypes.func,
    _dashprivate_layout: PropTypes.object,
    _dashprivate_loadingState: PropTypes.object,
    _dashprivate_paths: PropTypes.any,
    _dashprivate_requestQueue: PropTypes.any,
};

function isLoadingComponent(layout) {
    return Registry.resolve(layout.type, layout.namespace)._dashprivate_isLoadingComponent;
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

export const AugmentedTreeContainer = connect(
    state => ({
        dependencies: state.dependenciesRequest.content,
        paths: state.paths,
        requestQueue: state.requestQueue
    }),
    dispatch => ({dispatch}),
    (stateProps, dispatchProps, ownProps) => ({
        _dashprivate_dependencies: stateProps.dependencies,
        _dashprivate_dispatch: dispatchProps.dispatch,
        _dashprivate_layout: ownProps._dashprivate_layout,
        _dashprivate_loadingState: getLoadingState(ownProps._dashprivate_layout, stateProps.requestQueue),
        _dashprivate_paths: stateProps.paths,
        _dashprivate_requestQueue: stateProps.requestQueue,
    })
)(TreeContainer);

export default AugmentedTreeContainer;