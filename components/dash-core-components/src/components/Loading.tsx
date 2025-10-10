import React, {useState, useRef, useMemo, useEffect} from 'react';
import {equals, concat, includes, toPairs, any} from 'ramda';

import GraphSpinner from '../fragments/Loading/spinners/GraphSpinner';
import DefaultSpinner from '../fragments/Loading/spinners/DefaultSpinner';
import CubeSpinner from '../fragments/Loading/spinners/CubeSpinner';
import CircleSpinner from '../fragments/Loading/spinners/CircleSpinner';
import DotSpinner from '../fragments/Loading/spinners/DotSpinner';
import {LoadingProps} from 'src/types';
import {DebugTitleProps} from '../fragments/Loading/types';
import {DashLayoutPath} from '@dash-renderer/types/component';

const spinnerComponentOptions = {
    graph: GraphSpinner,
    cube: CubeSpinner,
    circle: CircleSpinner,
    dot: DotSpinner,
    default: DefaultSpinner,
} as const;

const getSpinner = (spinnerType: keyof typeof spinnerComponentOptions) =>
    spinnerComponentOptions[spinnerType];

const coveringSpinner: React.CSSProperties = {
    visibility: 'visible',
    position: 'absolute',
    top: '0',
    height: '100%',
    width: '100%',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
};

type LoadingState = {
    loading: Record<string, DebugTitleProps[]>;
};

const loadingSelector =
    (
        componentPath: DashLayoutPath,
        targetComponents?: Record<string, string | string[]>
    ) =>
    (state: LoadingState): DebugTitleProps[] | null => {
        let stringPath = JSON.stringify(componentPath);
        // Remove the last ] for easy match and add `,` to make sure only children
        // trigger the loading. See issue: https://github.com/plotly/dash/issues/3276
        stringPath = stringPath.substring(0, stringPath.length - 1) + ',';
        const loadingChildren = toPairs(state.loading).reduce(
            (acc, [path, load]) => {
                if (path.startsWith(stringPath) && load.length) {
                    if (
                        targetComponents &&
                        !any((l: DebugTitleProps) => {
                            const target = targetComponents[l.id];
                            if (!target) {
                                return false;
                            }
                            if (target === '*') {
                                return true;
                            }
                            if (Array.isArray(target)) {
                                return includes(l.property, target);
                            }
                            return l.property === target;
                        }, load)
                    ) {
                        return acc;
                    }
                    return concat(acc, load);
                }
                return acc;
            },
            [] as DebugTitleProps[]
        );
        if (loadingChildren.length) {
            return loadingChildren;
        }
        return null;
    };

function Loading({
    children,
    display = 'auto',
    color = 'var(--Dash-Fill-Interactive-Strong)',
    id,
    className,
    style,
    parent_className,
    parent_style,
    overlay_style,
    fullscreen,
    debug,
    show_initially = true,
    type: spinnerType = 'default',
    delay_hide = 0,
    delay_show = 0,
    target_components,
    custom_spinner,
}: LoadingProps) {
    const ctx = window.dash_component_api.useDashContext();

    const loading = ctx.useSelector(
        loadingSelector(ctx.componentPath, target_components),
        equals
    );

    const [showSpinner, setShowSpinner] = useState(show_initially);
    const dismissTimer = useRef<number | void>();
    const showTimer = useRef<number | void>();

    const containerStyle: React.CSSProperties = useMemo(() => {
        if (showSpinner) {
            return {visibility: 'hidden', ...overlay_style, ...parent_style};
        }
        return parent_style ?? {};
    }, [showSpinner, parent_style]);

    useEffect(() => {
        if (display === 'show' || display === 'hide') {
            setShowSpinner(display === 'show');
            return;
        }

        if (loading) {
            // if component is currently loading and there's a dismiss timer active
            // we need to clear it.
            if (dismissTimer.current) {
                dismissTimer.current = window.clearTimeout(
                    dismissTimer.current
                );
            }
            // if component is currently loading but the spinner is not showing and
            // there is no timer set to show, then set a timeout to show
            if (!showSpinner && !showTimer.current) {
                showTimer.current = window.setTimeout(() => {
                    setShowSpinner(true);
                    showTimer.current = undefined;
                }, delay_show);
            }
        } else {
            // if component is not currently loading and there's a show timer
            // active we need to clear it
            if (showTimer.current) {
                showTimer.current = window.clearTimeout(showTimer.current);
            }
            // if component is not currently loading and the spinner is showing and
            // there's no timer set to dismiss it, then set a timeout to hide it
            if (showSpinner && !dismissTimer.current) {
                dismissTimer.current = window.setTimeout(() => {
                    setShowSpinner(false);
                    dismissTimer.current = undefined;
                }, delay_hide);
            }
        }
    }, [delay_hide, delay_show, loading, display, showSpinner]);

    const Spinner = getSpinner(spinnerType);

    return (
        <div
            style={{position: 'relative', ...parent_style}}
            className={parent_className}
        >
            <div className={parent_className} style={containerStyle}>
                {children}
            </div>
            <div id={id} style={showSpinner ? coveringSpinner : {}}>
                {showSpinner &&
                    (custom_spinner || (
                        <Spinner
                            className={className}
                            style={style}
                            status={loading}
                            color={color}
                            debug={debug}
                            fullscreen={fullscreen}
                        />
                    ))}
            </div>
        </div>
    );
}

export default Loading;
