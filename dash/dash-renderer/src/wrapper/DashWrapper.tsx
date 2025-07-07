import React, {useCallback, MutableRefObject, useRef, useMemo} from 'react';
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
import {
    createElement,
    getComponentLayout,
    isDryComponent,
    checkRenderTypeProp,
    stringifyPath
} from './wrapping';
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
    _passedComponent?: any;
    _newRender?: any;
};

// Define a type for the memoized keys
type MemoizedKeysType = {
    [key: string]: React.ReactNode | null; // This includes React elements, strings, numbers, etc.
};

function DashWrapper({
    componentPath,
    _dashprivate_error,
    _passedComponent, // pass component to the DashWrapper in the event that it is a newRender and there are no layouthashes
    _newRender, // this is to force the component to newly render regardless of props (redraw and component as props) is passed from the parent
    ...extras
}: DashWrapperProps) {
    const dispatch = useDispatch();
    const memoizedKeys: MutableRefObject<MemoizedKeysType> = useRef({});
    const newRender = useRef(false);
    const renderedPath = useRef<DashLayoutPath>(componentPath);
    let renderComponent: any = null;
    let renderComponentProps: any = null;
    let renderH: any = null;

    // Get the config for the component as props
    const config: DashConfig = useSelector(selectConfig);

    // Select component and it's props, along with render hash, changed props and the reason for render
    const [component, componentProps, h, changedProps, renderType] =
        useSelector(selectDashProps(componentPath), selectDashPropsEqualityFn);

    renderComponent = component;
    renderComponentProps = componentProps;
    renderH = h;

    useMemo(() => {
        if (_newRender) {
            newRender.current = true;
            renderH = 0;
            if (renderH in memoizedKeys.current) {
                delete memoizedKeys.current[renderH];
            }
        } else {
            newRender.current = false;
        }
        renderedPath.current = componentPath;
    }, [_newRender]);

    const setProps = (newProps: UpdatePropsPayload) => {
        const {id} = renderComponentProps;
        const {_dash_error, ...restProps} = newProps;

        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        dispatch((dispatch, getState) => {
            const currentState = getState();
            const {graphs} = currentState;
            const oldLayout = getComponentLayout(
                renderedPath.current,
                currentState
            );
            if (!oldLayout) return;
            const {props: oldProps} = oldLayout;
            if (!oldProps) return;
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
                        itempath: renderedPath.current,
                        renderType: 'internal'
                    })
                );
            });
        });
    };

    const createContainer = useCallback(
        (container, containerPath, _childNewRender) => {
            if (isSimpleComponent(renderComponent)) {
                return renderComponent;
            }
            return (
                <DashWrapper
                    key={
                        container?.props?.id
                            ? stringifyId(container.props.id)
                            : stringifyPath(containerPath)
                    }
                    _dashprivate_error={_dashprivate_error}
                    componentPath={containerPath}
                    _passedComponent={container}
                    _newRender={_childNewRender}
                />
            );
        },
        []
    );

    const wrapChildrenProp = useCallback(
        (node: any, childrenPath: DashLayoutPath, _childNewRender: any) => {
            if (Array.isArray(node)) {
                return node.map((n, i) => {
                    if (isDryComponent(n)) {
                        return createContainer(
                            n,
                            concat(componentPath, [
                                'props',
                                ...childrenPath,
                                i
                            ]),
                            _childNewRender
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
                concat(componentPath, ['props', ...childrenPath]),
                _childNewRender
            );
        },
        [componentPath]
    );

    const extraProps = {
        setProps,
        ...extras
    } as {[key: string]: any};

    if (checkRenderTypeProp(renderComponent)) {
        extraProps['dashRenderType'] = newRender.current
            ? 'parent'
            : changedProps
            ? renderType
            : 'parent';
    }

    const setHydratedProps = (component: any, componentProps: any) => {
        // Hydrate components props
        const childrenProps = pathOr(
            [],
            ['children_props', component?.namespace, component?.type],
            config
        );
        let props = mergeRight(dissoc('children', componentProps), extraProps);

        for (let i = 0; i < childrenProps.length; i++) {
            const childrenProp: string = childrenProps[i];
            let childNewRender: any = 0;
            if (
                childrenProp
                    .split('.')[0]
                    .replace('[]', '')
                    .replace('{}', '') in changedProps ||
                newRender.current ||
                !renderH
            ) {
                childNewRender = {};
            }
            const handleObject = (obj: any, opath: DashLayoutPath) => {
                return mapObjIndexed(
                    (node, k) =>
                        wrapChildrenProp(node, [...opath, k], childNewRender),
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
                                elementPath,
                                childNewRender
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
                                            : concat(dynamic, [k]),
                                        childNewRender
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
                        nodeValue = wrapChildrenProp(
                            node,
                            childrenPath,
                            childNewRender
                        );
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
                            wrapChildrenProp(
                                node,
                                [childrenProp],
                                childNewRender
                            ),
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
    };

    const hydrateFunc = () => {
        if (newRender.current) {
            renderComponent = _passedComponent;
            renderComponentProps = _passedComponent?.props;
        }
        if (!renderComponent) {
            return null;
        }

        const element = Registry.resolve(renderComponent);
        const hydratedProps = setHydratedProps(
            renderComponent,
            renderComponentProps
        );

        let hydratedChildren: any;
        if (renderComponentProps.children !== undefined) {
            hydratedChildren = wrapChildrenProp(
                renderComponentProps.children,
                ['children'],
                !renderH || newRender.current || 'children' in changedProps
                    ? {}
                    : 0
            );
        }
        newRender.current = false;

        return config.props_check ? (
            <CheckedComponent
                element={element}
                props={hydratedProps}
                component={renderComponent}
            >
                {createElement(
                    element,
                    hydratedProps,
                    extraProps,
                    hydratedChildren
                )}
            </CheckedComponent>
        ) : (
            createElement(element, hydratedProps, extraProps, hydratedChildren)
        );
    };

    let hydrated = null;
    if (renderH in memoizedKeys.current && !newRender.current) {
        hydrated = React.isValidElement(memoizedKeys.current[renderH])
            ? memoizedKeys.current[renderH]
            : null;
    }
    if (!hydrated) {
        hydrated = hydrateFunc();
        memoizedKeys.current = {[renderH]: hydrated};
    }

    return renderComponent ? (
        <ComponentErrorBoundary
            componentType={renderComponent.type}
            componentId={
                is(Object, renderComponentProps.id)
                    ? stringifyId(renderComponentProps.id)
                    : renderComponentProps.id
            }
            error={_dashprivate_error}
            dispatch={dispatch}
        >
            <DashContextProvider componentPath={componentPath}>
                {React.isValidElement(hydrated) ? hydrated : <div />}
            </DashContextProvider>
        </ComponentErrorBoundary>
    ) : (
        <div />
    );
}

export default DashWrapper;
