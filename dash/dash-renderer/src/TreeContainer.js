import React, {Component, memo} from 'react';
import PropTypes from 'prop-types';
import Registry from './registry';
import {propTypeErrorHandler} from './exceptions';
import {
    addIndex,
    concat,
    dissoc,
    equals,
    isEmpty,
    isNil,
    keys,
    map,
    mergeRight,
    pick,
    pickBy,
    propOr,
    type
} from 'ramda';
import {notifyObservers, updateProps} from './actions';
import isSimpleComponent from './isSimpleComponent';
import {recordUiEdit} from './persistence';
import ComponentErrorBoundary from './components/error/ComponentErrorBoundary.react';
import checkPropTypes from './checkPropTypes';
import {getWatchedKeys, stringifyId} from './actions/dependencies';
import {
    getLoadingHash,
    getLoadingState,
    validateComponent
} from './utils/TreeContainer';
import {DashContext} from './APIController.react';
import {deserializeProps} from './serializers/utils';

const NOT_LOADING = {
    is_loading: false
};

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
    id: PropTypes.string
};

function createElement(element, props, extraProps, children) {
    const allProps = mergeRight(props, extraProps);
    if (Array.isArray(children)) {
        return React.createElement(element, allProps, ...children);
    }
    return React.createElement(element, allProps, children);
}

const TreeContainer = memo(props => (
    <DashContext.Consumer>
        {context => (
            <BaseTreeContainer
                {...context.fn()}
                {...props}
                _dashprivate_path={JSON.parse(props._dashprivate_path)}
            />
        )}
    </DashContext.Consumer>
));

class BaseTreeContainer extends Component {
    constructor(props) {
        super(props);

        this.setProps = this.setProps.bind(this);
    }

    createContainer(props, component, path) {
        if (isSimpleComponent(component)) {
            return component;
        }
        return (
            <TreeContainer
                key={
                    component &&
                    component.props &&
                    stringifyId(component.props.id)
                }
                _dashprivate_error={props._dashprivate_error}
                _dashprivate_layout={component}
                _dashprivate_loadingState={getLoadingState(
                    component,
                    path,
                    props._dashprivate_loadingMap
                )}
                _dashprivate_loadingStateHash={getLoadingHash(
                    path,
                    props._dashprivate_loadingMap
                )}
                _dashprivate_path={JSON.stringify(path)}
            />
        );
    }

    setProps(newProps) {
        const {
            _dashprivate_graphs,
            _dashprivate_dispatch,
            _dashprivate_path,
            _dashprivate_layout
        } = this.props;

        const oldProps = this.getLayoutProps();
        const {id} = oldProps;
        const changedProps = pickBy(
            (val, key) => !equals(val, oldProps[key]),
            newProps
        );
        if (!isEmpty(changedProps)) {
            // Identify the modified props that are required for callbacks
            const watchedKeys = getWatchedKeys(
                id,
                keys(changedProps),
                _dashprivate_graphs
            );

            // setProps here is triggered by the UI - record these changes
            // for persistence
            recordUiEdit(_dashprivate_layout, newProps, _dashprivate_dispatch);

            // Only dispatch changes to Dash if a watched prop changed
            if (watchedKeys.length) {
                _dashprivate_dispatch(
                    notifyObservers({
                        id,
                        props: pick(watchedKeys, changedProps)
                    })
                );
            }

            // Always update this component's props
            _dashprivate_dispatch(
                updateProps({
                    props: changedProps,
                    itempath: _dashprivate_path
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
                      this.createContainer(
                          this.props,
                          component,
                          concat(path, ['props', 'children', i])
                      ),
                  components
              )
            : this.createContainer(
                  this.props,
                  components,
                  concat(path, ['props', 'children'])
              );
    }

    getComponent(_dashprivate_layout, children, loading_state, setProps) {
        const {_dashprivate_config, _dashprivate_dispatch, _dashprivate_error} =
            this.props;

        if (isEmpty(_dashprivate_layout)) {
            return null;
        }

        if (isSimpleComponent(_dashprivate_layout)) {
            return _dashprivate_layout;
        }

        validateComponent(_dashprivate_layout);

        const element = Registry.resolve(_dashprivate_layout);

        const original_props = dissoc('children', _dashprivate_layout.props);

        if (type(original_props.id) === 'Object') {
            // Turn object ids (for wildcards) into unique strings.
            // Because of the `dissoc` above we're not mutating the layout,
            // just the id we pass on to the rendered component
            original_props.id = stringifyId(original_props.id);
        }
        const _initial_extraProps = {
            loading_state: loading_state || NOT_LOADING,
            setProps
        };

        /*
            This should be the best place to hook the given `props` values for each component,
            then strip any serialized values and create bookkeepers for `__type`s
        */
        const {props, extraProps} = deserializeProps(
            original_props,
            _initial_extraProps
        );

        // console.log('!!! getComponent: got props: ', props, '\n extraProps: ', extraProps)

        return (
            <ComponentErrorBoundary
                componentType={_dashprivate_layout.type}
                componentId={props.id}
                key={props.id}
                dispatch={_dashprivate_dispatch}
                error={_dashprivate_error}
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

    getLayoutProps() {
        return propOr({}, 'props', this.props._dashprivate_layout);
    }

    render() {
        const {
            _dashprivate_layout,
            _dashprivate_loadingState,
            _dashprivate_path
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
    _dashprivate_error: PropTypes.any,
    _dashprivate_layout: PropTypes.object,
    _dashprivate_loadingState: PropTypes.oneOfType([
        PropTypes.object,
        PropTypes.bool
    ]),
    _dashprivate_loadingStateHash: PropTypes.string,
    _dashprivate_path: PropTypes.string
};

BaseTreeContainer.propTypes = {
    ...TreeContainer.propTypes,
    _dashprivate_config: PropTypes.object,
    _dashprivate_dispatch: PropTypes.func,
    _dashprivate_graphs: PropTypes.any,
    _dashprivate_loadingMap: PropTypes.any,
    _dashprivate_path: PropTypes.array
};

export default TreeContainer;
