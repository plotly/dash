import React, {
    useCallback,
    MutableRefObject,
    useRef,
    useMemo,
    useEffect
} from 'react';
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
import {
    notifyObservers,
    onError,
    updateProps,
    resetComponentState
} from '../actions';
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

// Identity of a dash component: which component it is, not what its
// current prop values are. Used to decide between remounting (identity
// changed) and reconciling in place (same component, new props).
const componentIdentity = (component: any) => {
    const id = component?.props?.id;
    return `${component?.namespace}.${component?.type}.${
        id ? stringifyId(id) : ''
    }`;
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
    const freshRenders = useRef(0);
    // Did *this* render remount the subtree (identity changed or an explicit
    // dash.remount())? A remount rebuilds every descendant from scratch, so
    // the item-by-item ref-skip below must not carry anything over across it.
    const remountedThisRender = useRef(false);
    const renderedIdentity: MutableRefObject<string | null> = useRef(null);
    const hasFreshRendered = useRef(false);
    const renderedPath = useRef<DashLayoutPath>(componentPath);
    // Previous array value of each children-like prop this component
    // hydrated, keyed by childrenPath. Lets wrapChildrenProp recognize
    // items that are the exact same object as last time (eg. every
    // pre-existing item in a list a Patch only appended to), so they can
    // keep reconciling in place instead of being forced to re-hydrate their
    // whole subtree just because a sibling was added.
    const prevChildrenArrays: MutableRefObject<{[key: string]: any[]}> = useRef(
        {}
    );
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
            // Only force a remount (via the `key` bump below) when the
            // component identity at this path actually changed. When the
            // same component is passed again (eg: a callback returning
            // updated children with the same structure), reconcile in
            // place instead of unmounting the whole subtree. (#3846)
            //
            // `_dashprivate_remount` is set by `dash.remount()` and forces
            // a remount even when the identity is unchanged, letting a
            // callback explicitly reset a component's internal state.
            const identity = componentIdentity(_passedComponent);
            const isRemount = Boolean(
                _passedComponent?._dashprivate_remount ||
                    (renderedIdentity.current !== null &&
                        renderedIdentity.current !== identity)
            );
            remountedThisRender.current = isRemount;
            if (isRemount) {
                freshRenders.current += 1;
            }
            renderedIdentity.current = identity;
            if (renderH in memoizedKeys.current) {
                delete memoizedKeys.current[renderH];
            }
        } else {
            newRender.current = false;
            remountedThisRender.current = false;
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
        (
            node: any,
            childrenPath: DashLayoutPath,
            _childNewRender: any,
            allowRefSkip = false
        ) => {
            if (Array.isArray(node)) {
                const pathKey = stringifyPath(childrenPath);
                const prevArray = allowRefSkip
                    ? prevChildrenArrays.current[pathKey]
                    : undefined;
                prevChildrenArrays.current[pathKey] = node;
                return node.map((n, i) => {
                    if (isDryComponent(n)) {
                        // An item that's the exact same object as before
                        // didn't change - not even props a shallow patch
                        // analysis might miss - so it doesn't need to be
                        // forced into a fresh hydrate just because this array
                        // as a whole did (eg. a sibling got appended, or a
                        // deeper list this item sits above grew: ramda's
                        // assocPath rebuilds the array and this item's parent
                        // on the way to the change, but `concat` keeps the
                        // pre-existing items themselves the same object).
                        const unchanged = allowRefSkip && prevArray?.[i] === n;
                        return createContainer(
                            n,
                            concat(componentPath, [
                                'props',
                                ...childrenPath,
                                i
                            ]),
                            unchanged ? 0 : _childNewRender
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

    useEffect(() => {
        if (_newRender) {
            // Don't reset descendant layout hashes on the component's very
            // first fresh render: components that set their initial state on
            // mount (eg. dbc Tabs picking the default active tab) would have
            // that state wiped before it takes effect. Stale descendant
            // hashes are only a concern once the subtree has rendered at
            // least once, so reset from the second fresh render onward.
            // (#3929, keeps #3330 fixed.)
            if (hasFreshRendered.current) {
                dispatch(
                    resetComponentState({
                        itempath: componentPath
                    })
                );
            }
            hasFreshRendered.current = true;
        }
    }, [_newRender]);

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
                    : 0,
                // Check items one by one against the previous render whenever
                // we're not remounting. Even a component getting a fresh
                // hydrate (eg. a Patch appended a deep sibling, so its parent
                // was rebuilt on the path down) can keep the pre-existing
                // items - the exact same objects - reconciling in place
                // instead of re-hydrating the whole list every time. A first
                // render simply has no previous array to match, and a remount
                // must rebuild everything, so both fall through to a fresh
                // hydrate.
                !remountedThisRender.current
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
            key={freshRenders.current}
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
