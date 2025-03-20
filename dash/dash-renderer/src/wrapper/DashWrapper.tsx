import React, {useMemo, useCallback, memo} from 'react';
import {
    path,
    concat,
    pickBy,
    equals,
    keys,
    is,
    isEmpty,
    pick,
    assocPath,
    pathOr,
    mergeRight,
    dissoc,
    assoc,
    mapObjIndexed,
    type
} from 'ramda';
import {useSelector, useDispatch, batch} from 'react-redux';

import ComponentErrorBoundary from '../components/error/ComponentErrorBoundary.react';
import {DashLayoutPath, UpdatePropsPayload} from '../types/component';
import {DashConfig} from '../config';
import {notifyObservers, onError, updateProps} from '../actions';
import {getWatchedKeys, stringifyId} from '../actions/dependencies';
import {recordUiEdit} from '../persistence';
import {createElement, getComponentLayout, isDryComponent} from './wrapping';
import Registry from '../registry';
import isSimpleComponent from '../isSimpleComponent';
import {
    selectDashProps,
    selectDashPropsEqualityFn,
    selectConfig
} from './selectors';
import CheckedComponent from './CheckedComponent';
import {DashContextProvider} from './DashContext';

type DashWrapperProps = {
    /**
     * Path of the component in the layout.
     */
    componentPath: DashLayoutPath;
    _dashprivate_error?: any;
};

function DashWrapper({
    componentPath,
    _dashprivate_error,
    ...extras
}: DashWrapperProps) {
    const dispatch = useDispatch();

    // Get the config for the component as props
    const config: DashConfig = useSelector(selectConfig);

    // Select both the component and it's props.
    const [component, componentProps] = useSelector(
        selectDashProps(componentPath),
        selectDashPropsEqualityFn
    );

    const setProps = (newProps: UpdatePropsPayload) => {
        const {id} = componentProps;
        const {_dash_error, ...restProps} = newProps;

        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        dispatch((dispatch, getState) => {
            const currentState = getState();
            const {graphs} = currentState;

            const {props: oldProps} = getComponentLayout(
                componentPath,
                currentState
            );
            const changedProps = pickBy(
                (val, key) => !equals(val, oldProps[key]),
                restProps
            );
            if (_dash_error) {
                dispatch(
                    onError({
                        type: 'frontEnd',
                        error: _dash_error
                    })
                );
            }

            if (isEmpty(changedProps)) {
                return;
            }

            // Identify the modified props that are required for callbacks
            const watchedKeys = getWatchedKeys(id, keys(changedProps), graphs);

            batch(() => {
                // setProps here is triggered by the UI - record these changes
                // for persistence
                recordUiEdit(component, newProps, dispatch);

                // Only dispatch changes to Dash if a watched prop changed
                if (watchedKeys.length) {
                    dispatch(
                        notifyObservers({
                            id,
                            props: pick(watchedKeys, changedProps)
                        })
                    );
                }

                // Always update this component's props
                dispatch(
                    updateProps({
                        props: changedProps,
                        itempath: componentPath
                    })
                );
            });
        });
    };

    const createContainer = useCallback(
        (container, containerPath, key = undefined) => {
            if (isSimpleComponent(component)) {
                return component;
            }
            return (
                <DashWrapper
                    key={
                        (container &&
                            container.props &&
                            stringifyId(container.props.id)) ||
                        key
                    }
                    _dashprivate_error={_dashprivate_error}
                    componentPath={containerPath}
                />
            );
        },
        []
    );

    const wrapChildrenProp = useCallback(
        (node: any, childrenProp: DashLayoutPath) => {
            if (Array.isArray(node)) {
                return node.map((n, i) => {
                    if (isDryComponent(n)) {
                        return createContainer(
                            n,
                            concat(componentPath, [
                                'props',
                                ...childrenProp,
                                i
                            ]),
                            i
                        );
                    }
                    return n;
                });
            }
            if (!isDryComponent(node)) {
                return node;
            }
            return createContainer(
                node,
                concat(componentPath, ['props', ...childrenProp])
            );
        },
        [componentPath]
    );

    const extraProps = {
        setProps,
        ...extras
    };

    const element = useMemo(() => Registry.resolve(component), [component]);

    const hydratedProps = useMemo(() => {
        // Hydrate components props
        const childrenProps = pathOr(
            [],
            ['children_props', component.namespace, component.type],
            config
        );
        let props = mergeRight(dissoc('children', componentProps), extraProps);

        for (let i = 0; i < childrenProps.length; i++) {
            const childrenProp: string = childrenProps[i];

            const handleObject = (obj: any, opath: DashLayoutPath) => {
                return mapObjIndexed(
                    (node, k) => wrapChildrenProp(node, [...opath, k]),
                    obj
                );
            };

            if (childrenProp.includes('.')) {
                let childrenPath: DashLayoutPath = childrenProp.split('.');
                let node: any;
                let nodeValue: any;
                if (childrenProp.includes('[]')) {
                    const frontPath: string[] = [],
                        backPath: string[] = [];
                    let found = false,
                        hasObject = false;
                    // At first the childrenPath is always a list of strings.
                    (childrenPath as string[]).forEach(p => {
                        if (!found) {
                            if (p.includes('[]')) {
                                found = true;
                                if (p.includes('{}')) {
                                    hasObject = true;
                                    frontPath.push(
                                        p.replace('{}', '').replace('[]', '')
                                    );
                                } else {
                                    frontPath.push(p.replace('[]', ''));
                                }
                            } else if (p.includes('{}')) {
                                hasObject = true;
                                frontPath.push(p.replace('{}', ''));
                            } else {
                                frontPath.push(p);
                            }
                        } else {
                            if (p.includes('{}')) {
                                hasObject = true;
                                backPath.push(p.replace('{}', ''));
                            } else {
                                backPath.push(p);
                            }
                        }
                    });

                    node = path(frontPath, props);
                    if (node === undefined || !node?.length) {
                        continue;
                    }
                    const firstNode = path(backPath, node[0]);
                    if (!firstNode) {
                        continue;
                    }

                    nodeValue = node.map((el: any, i: number) => {
                        const elementPath = concat(
                            frontPath,
                            concat([i], backPath)
                        );
                        let listValue;
                        if (hasObject) {
                            if (backPath.length) {
                                listValue = handleObject(
                                    path(backPath, el),
                                    elementPath
                                );
                            } else {
                                listValue = handleObject(el, elementPath);
                            }
                        } else {
                            listValue = wrapChildrenProp(
                                path(backPath, el),
                                elementPath
                            );
                        }
                        return assocPath(backPath, listValue, el);
                    });
                    childrenPath = frontPath;
                } else {
                    if (childrenProp.includes('{}')) {
                        // Only supports one level of nesting.
                        const front = [];
                        let dynamic: DashLayoutPath = [];
                        let hasBack = false;
                        const backPath: DashLayoutPath = [];

                        for (let j = 0; j < childrenPath.length; j++) {
                            const cur = childrenPath[j] as string;
                            if (cur.includes('{}')) {
                                dynamic = concat(front, [
                                    cur.replace('{}', '')
                                ]);
                                if (j < childrenPath.length - 1) {
                                    hasBack = true;
                                }
                            } else {
                                if (hasBack) {
                                    backPath.push(cur);
                                } else {
                                    front.push(cur);
                                }
                            }
                        }

                        const dynValue = path(dynamic, props);
                        if (dynValue !== undefined) {
                            // too dynamic for proper ts.
                            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                            // @ts-ignore
                            nodeValue = mapObjIndexed(
                                (d, k) =>
                                    wrapChildrenProp(
                                        hasBack ? path(backPath, d) : d,
                                        hasBack
                                            ? concat(
                                                  dynamic,
                                                  concat([k], backPath)
                                              )
                                            : concat(dynamic, [k])
                                    ),
                                dynValue
                            );
                            childrenPath = dynamic;
                        }
                    } else {
                        node = path(childrenPath, props);
                        if (node === undefined) {
                            continue;
                        }
                        nodeValue = wrapChildrenProp(node, childrenPath);
                    }
                }
                props = assocPath(childrenPath, nodeValue, props);
            } else {
                if (childrenProp.includes('{}')) {
                    let opath = childrenProp.replace('{}', '');
                    const isArray = childrenProp.includes('[]');
                    if (isArray) {
                        opath = opath.replace('[]', '');
                    }
                    const node = props[opath];

                    if (node !== undefined) {
                        if (isArray) {
                            for (let j = 0; j < node.length; j++) {
                                const aPath = concat([opath], [j]);
                                props = assocPath(
                                    aPath,
                                    handleObject(node[j], aPath),
                                    props
                                );
                            }
                        } else {
                            props = assoc(
                                opath,
                                handleObject(node, [opath]),
                                props
                            );
                        }
                    }
                } else {
                    const node = props[childrenProp];
                    if (node !== undefined) {
                        props = assoc(
                            childrenProp,
                            wrapChildrenProp(node, [childrenProp]),
                            props
                        );
                    }
                }
            }
        }
        if (type(props.id) === 'Object') {
            // Turn object ids (for wildcards) into unique strings.
            // Because of the `dissoc` above we're not mutating the layout,
            // just the id we pass on to the rendered component
            props.id = stringifyId(props.id);
        }
        return props;
    }, [componentProps]);

    const hydrated = useMemo(() => {
        let hydratedChildren: any;
        if (componentProps.children !== undefined) {
            hydratedChildren = wrapChildrenProp(componentProps.children, [
                'children'
            ]);
        }
        if (config.props_check) {
            return (
                <CheckedComponent
                    element={element}
                    props={hydratedProps}
                    component={component}
                >
                    {createElement(
                        element,
                        hydratedProps,
                        extraProps,
                        hydratedChildren
                    )}
                </CheckedComponent>
            );
        }

        return createElement(
            element,
            hydratedProps,
            extraProps,
            hydratedChildren
        );
    }, [
        element,
        component,
        hydratedProps,
        extraProps,
        wrapChildrenProp,
        componentProps,
        config.props_check
    ]);

    return (
        <ComponentErrorBoundary
            componentType={component.type}
            componentId={
                is(Object, componentProps.id)
                    ? stringifyId(componentProps.id)
                    : componentProps.id
            }
            error={_dashprivate_error}
            dispatch={dispatch}
        >
            <DashContextProvider componentPath={componentPath}>
                {hydrated}
            </DashContextProvider>
        </ComponentErrorBoundary>
    );
}

function wrapperEquality(prev: any, next: any) {
    const {
        componentPath: prevPath,
        _dashprivate_error: prevError,
        ...prevProps
    } = prev;
    const {
        componentPath: nextPath,
        _dashprivate_error: nextError,
        ...nextProps
    } = next;
    if (JSON.stringify(prevPath) !== JSON.stringify(nextPath)) {
        return false;
    }
    if (prevError !== nextError) {
        return false;
    }
    return equals(prevProps, nextProps);
}

export default memo(DashWrapper, wrapperEquality);
