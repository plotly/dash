import React, {Component} from 'react';
import PropTypes from 'prop-types';
import Registry from './registry';
import {propTypeErrorHandler} from './exceptions';
import {connect} from 'react-redux';
import {
    addIndex,
    concat,
    dissoc,
    equals,
    filter,
    has,
    isEmpty,
    isNil,
    keys,
    map,
    mergeRight,
    pick,
    pickBy,
    propOr,
    type,
} from 'ramda';
import {notifyObservers, updateProps} from './actions';
import isSimpleComponent from './isSimpleComponent';
import {recordUiEdit} from './persistence';
import ComponentErrorBoundary from './components/error/ComponentErrorBoundary.react';
import checkPropTypes from './checkPropTypes';
import {getWatchedKeys, stringifyId} from './actions/dependencies';

function validateComponent(componentDefinition) {
    if (type(componentDefinition) === 'Array') {
        throw new Error(
            'The children property of a component is a list of lists, instead ' +
                'of just a list. ' +
                'Check the component that has the following contents, ' +
                'and remove one of the levels of nesting: \n' +
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
            key={
                component && component.props && stringifyId(component.props.id)
            }
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

    return createElement(element, props, extraProps, children);
}

CheckedComponent.propTypes = {
    children: PropTypes.any,
    element: PropTypes.any,
    layout: PropTypes.any,
    props: PropTypes.any,
    extraProps: PropTypes.any,
    id: PropTypes.string,
};

function createElement(element, props, extraProps, children) {
    const allProps = mergeRight(props, extraProps);
    if (Array.isArray(children)) {
        return React.createElement(element, allProps, ...children);
    }
    return React.createElement(element, allProps, children);
}

class TreeContainer extends Component {
    constructor(props) {
        super(props);

        this.setProps = this.setProps.bind(this);
    }

    setProps(newProps) {
        const {
            _dashprivate_graphs,
            _dashprivate_dispatch,
            _dashprivate_path,
            _dashprivate_layout,
        } = this.props;

        const oldProps = this.getLayoutProps();
        const {id} = oldProps;
        const changedProps = pickBy(
            (val, key) => !equals(val, oldProps[key]),
            newProps
        );
        const changedKeys = keys(changedProps);
        if (changedKeys.length) {
            // Identify the modified props that are required for callbacks
            const watchedKeys = getWatchedKeys(
                id,
                changedKeys,
                _dashprivate_graphs
            );

            // setProps here is triggered by the UI - record these changes
            // for persistence
            recordUiEdit(_dashprivate_layout, newProps, _dashprivate_dispatch);

            // Always update this component's props
            _dashprivate_dispatch(
                updateProps({
                    props: changedProps,
                    itempath: _dashprivate_path,
                })
            );

            // Only dispatch changes to Dash if a watched prop changed
            if (watchedKeys.length) {
                _dashprivate_dispatch(
                    notifyObservers({
                        id: id,
                        props: pick(watchedKeys, changedProps),
                    })
                );
            }
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

        const props = dissoc('children', _dashprivate_layout.props);

        if (type(props.id) === 'Object') {
            // Turn object ids (for wildcards) into unique strings.
            // Because of the `dissoc` above we're not mutating the layout,
            // just the id we pass on to the rendered component
            props.id = stringifyId(props.id);
        }
        const extraProps = {loading_state, setProps};

        return (
            <ComponentErrorBoundary
                componentType={_dashprivate_layout.type}
                componentId={props.id}
                key={props.id}
            >
                {_dashprivate_config.props_check ? (
                    <CheckedComponent
                        children={children}
                        element={element}
                        props={props}
                        extraProps={extraProps}
                        type={_dashprivate_layout.type}
                    />
                ) : (
                    createElement(element, props, extraProps, children)
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
    _dashprivate_graphs: PropTypes.any,
    _dashprivate_dispatch: PropTypes.func,
    _dashprivate_layout: PropTypes.object,
    _dashprivate_loadingState: PropTypes.object,
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

function getLoadingState(layout, pendingCallbacks) {
    const ids = isLoadingComponent(layout)
        ? getNestedIds(layout)
        : layout && layout.props.id && [layout.props.id];

    let isLoading = false;
    let loadingProp;
    let loadingComponent;

    if (pendingCallbacks && pendingCallbacks.length && ids && ids.length) {
        const idStrs = ids.map(stringifyId);

        pendingCallbacks.forEach(cb => {
            const {requestId, requestedOutputs} = cb;
            if (requestId === undefined) {
                return;
            }

            idStrs.forEach(idStr => {
                const props = requestedOutputs[idStr];
                if (props) {
                    isLoading = true;
                    // TODO: what about multiple loading components / props?
                    loadingComponent = idStr;
                    loadingProp = props[0];
                }
            });
        });
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
        graphs: state.graphs,
        pendingCallbacks: state.pendingCallbacks,
        config: state.config,
    }),
    dispatch => ({dispatch}),
    (stateProps, dispatchProps, ownProps) => ({
        _dashprivate_graphs: stateProps.graphs,
        _dashprivate_dispatch: dispatchProps.dispatch,
        _dashprivate_layout: ownProps._dashprivate_layout,
        _dashprivate_path: ownProps._dashprivate_path,
        _dashprivate_loadingState: getLoadingState(
            ownProps._dashprivate_layout,
            stateProps.pendingCallbacks
        ),
        _dashprivate_config: stateProps.config,
    })
)(TreeContainer);

export default AugmentedTreeContainer;
