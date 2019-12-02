import React, {Component} from 'react';
import PropTypes from 'prop-types';
import Registry from './registry';
import {propTypeErrorHandler} from './exceptions';
import {connect} from 'react-redux';
import {
    addIndex,
    any,
    concat,
    filter,
    forEach,
    has,
    includes,
    isEmpty,
    isNil,
    keysIn,
    map,
    mergeRight,
    omit,
    pick,
    propOr,
    type,
} from 'ramda';
import {notifyObservers, updateProps} from './actions';
import isSimpleComponent from './isSimpleComponent';
import {recordUiEdit} from './persistence';
import ComponentErrorBoundary from './components/error/ComponentErrorBoundary.react';
import checkPropTypes from './checkPropTypes';

function validateComponent(componentDefinition) {
    if (type(componentDefinition) === 'Array') {
        throw new Error(
            'The children property of a component is a list of lists, instead ' +
                'of just a list. ' +
                'Check the component that has the following contents, ' +
                'and remove of the levels of nesting: \n' +
                JSON.stringify(componentDefinition, null, 2)
        );
    }
    if (
        type(componentDefinition) === 'Object' &&
        !(
            has('namespace', componentDefinition) &&
            has('type', componentDefinition) &&
            has('props', componentDefinition)
        )
    ) {
        throw new Error(
            'An object was provided as `children` instead of a component, ' +
                'string, or number (or list of those). ' +
                'Check the children property that looks something like:\n' +
                JSON.stringify(componentDefinition, null, 2)
        );
    }
}

const createContainer = (component, path) =>
    isSimpleComponent(component) ? (
        component
    ) : (
        <AugmentedTreeContainer
            key={component && component.props && component.props.id}
            _dashprivate_layout={component}
            _dashprivate_path={path}
        />
    );

function CheckedComponent(p) {
    const {element, extraProps, props, children, type} = p;

    const errorMessage = checkPropTypes(
        element.propTypes,
        props,
        'component prop',
        element
    );
    if (errorMessage) {
        propTypeErrorHandler(errorMessage, props, type);
    }

    return React.createElement(
        element,
        mergeRight(props, extraProps),
        ...(Array.isArray(children) ? children : [children])
    );
}

CheckedComponent.propTypes = {
    children: PropTypes.any,
    element: PropTypes.any,
    layout: PropTypes.any,
    props: PropTypes.any,
    extraProps: PropTypes.any,
    id: PropTypes.string,
};
class TreeContainer extends Component {
    constructor(props) {
        super(props);

        this.setProps = this.setProps.bind(this);
    }

    setProps(newProps) {
        const {
            _dashprivate_dependencies,
            _dashprivate_dispatch,
            _dashprivate_path,
            _dashprivate_layout,
        } = this.props;

        const id = this.getLayoutProps().id;

        // Identify the modified props that are required for callbacks
        const watchedKeys = filter(
            key =>
                _dashprivate_dependencies &&
                _dashprivate_dependencies.find(
                    dependency =>
                        dependency.inputs.find(
                            input => input.id === id && input.property === key
                        ) ||
                        dependency.state.find(
                            state => state.id === id && state.property === key
                        )
                )
        )(keysIn(newProps));

        // setProps here is triggered by the UI - record these changes
        // for persistence
        recordUiEdit(_dashprivate_layout, newProps, _dashprivate_dispatch);

        // Always update this component's props
        _dashprivate_dispatch(
            updateProps({
                props: newProps,
                itempath: _dashprivate_path,
            })
        );

        // Only dispatch changes to Dash if a watched prop changed
        if (watchedKeys.length) {
            _dashprivate_dispatch(
                notifyObservers({
                    id: id,
                    props: pick(watchedKeys)(newProps),
                })
            );
        }
    }

    getChildren(components, path) {
        if (isNil(components)) {
            return null;
        }

        return Array.isArray(components)
            ? addIndex(map)(
                  (component, i) =>
                      createContainer(
                          component,
                          concat(path, ['props', 'children', i])
                      ),
                  components
              )
            : createContainer(components, concat(path, ['props', 'children']));
    }

    getComponent(_dashprivate_layout, children, loading_state, setProps) {
        const {_dashprivate_config} = this.props;

        if (isEmpty(_dashprivate_layout)) {
            return null;
        }

        if (isSimpleComponent(_dashprivate_layout)) {
            return _dashprivate_layout;
        }
        validateComponent(_dashprivate_layout);

        const element = Registry.resolve(_dashprivate_layout);

        const props = omit(['children'], _dashprivate_layout.props);

        return _dashprivate_config.props_check ? (
            <ComponentErrorBoundary
                componentType={_dashprivate_layout.type}
                componentId={_dashprivate_layout.props.id}
                key={element && element.props && element.props.id}
            >
                <CheckedComponent
                    children={children}
                    element={element}
                    props={props}
                    extraProps={{loading_state, setProps}}
                    type={_dashprivate_layout.type}
                />
            </ComponentErrorBoundary>
        ) : (
            <ComponentErrorBoundary
                componentType={_dashprivate_layout.type}
                componentId={_dashprivate_layout.props.id}
                key={element && element.props && element.props.id}
            >
                {React.createElement(
                    element,
                    mergeRight(props, {loading_state, setProps}),
                    ...(Array.isArray(children) ? children : [children])
                )}
            </ComponentErrorBoundary>
        );
    }

    shouldComponentUpdate(nextProps) {
        const {_dashprivate_layout, _dashprivate_loadingState} = nextProps;
        return (
            _dashprivate_layout !== this.props._dashprivate_layout ||
            _dashprivate_loadingState.is_loading !==
                this.props._dashprivate_loadingState.is_loading
        );
    }

    getLayoutProps() {
        return propOr({}, 'props', this.props._dashprivate_layout);
    }

    render() {
        const {
            _dashprivate_layout,
            _dashprivate_loadingState,
            _dashprivate_path,
        } = this.props;

        const layoutProps = this.getLayoutProps();

        const children = this.getChildren(
            layoutProps.children,
            _dashprivate_path
        );

        return this.getComponent(
            _dashprivate_layout,
            children,
            _dashprivate_loadingState,
            this.setProps
        );
    }
}

TreeContainer.propTypes = {
    _dashprivate_dependencies: PropTypes.any,
    _dashprivate_dispatch: PropTypes.func,
    _dashprivate_layout: PropTypes.object,
    _dashprivate_loadingState: PropTypes.object,
    _dashprivate_requestQueue: PropTypes.any,
    _dashprivate_config: PropTypes.object,
    _dashprivate_path: PropTypes.array,
};

function isLoadingComponent(layout) {
    validateComponent(layout);
    return Registry.resolve(layout)._dashprivate_isLoadingComponent;
}

function getNestedIds(layout) {
    const ids = [];
    const queue = [layout];

    while (queue.length) {
        const elementLayout = queue.shift();

        const props = elementLayout && elementLayout.props;

        if (!props) {
            continue;
        }

        const {children, id} = props;

        if (id) {
            ids.push(id);
        }

        if (children) {
            const filteredChildren = filter(
                child =>
                    !isSimpleComponent(child) && !isLoadingComponent(child),
                Array.isArray(children) ? children : [children]
            );

            queue.push(...filteredChildren);
        }
    }

    return ids;
}

function getLoadingState(layout, requestQueue) {
    const ids = isLoadingComponent(layout)
        ? getNestedIds(layout)
        : layout && layout.props.id
        ? [layout.props.id]
        : [];

    let isLoading = false;
    let loadingProp;
    let loadingComponent;

    if (requestQueue) {
        forEach(r => {
            const controllerId = isNil(r.controllerId) ? '' : r.controllerId;
            if (
                r.status === 'loading' &&
                any(id => includes(id, controllerId), ids)
            ) {
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
        requestQueue: state.requestQueue,
        config: state.config,
    }),
    dispatch => ({dispatch}),
    (stateProps, dispatchProps, ownProps) => ({
        _dashprivate_dependencies: stateProps.dependencies,
        _dashprivate_dispatch: dispatchProps.dispatch,
        _dashprivate_layout: ownProps._dashprivate_layout,
        _dashprivate_path: ownProps._dashprivate_path,
        _dashprivate_loadingState: getLoadingState(
            ownProps._dashprivate_layout,
            stateProps.requestQueue
        ),
        _dashprivate_requestQueue: stateProps.requestQueue,
        _dashprivate_config: stateProps.config,
    })
)(TreeContainer);

export default AugmentedTreeContainer;
