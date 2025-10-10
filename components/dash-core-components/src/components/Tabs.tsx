import React, {useCallback, useEffect, useRef, useState} from 'react';
import {has, isNil} from 'ramda';

import LoadingElement from '../utils/_LoadingElement';
import {PersistedProps, PersistenceTypes, TabProps, TabsProps} from '../types';
import './css/tabs.css';
import {DashComponent} from '@dash-renderer/types/component';

interface EnhancedTabProps extends TabProps {
    selected: boolean;
    componentPath?: (string | number)[];
}

// EnhancedTab is defined here instead of in Tab.tsx because if exported there,
// it will mess up the Python imports and metadata.json
const EnhancedTab = ({
    id,
    label,
    selected,
    className,
    style,
    selected_className,
    selected_style,
    setProps: selectHandler,
    value,
    disabled = false,
    disabled_style = {color: 'var(--Dash-Text-Disabled)'},
    disabled_className,
    componentPath,
}: EnhancedTabProps) => {
    const ExternalWrapper = window.dash_component_api.ExternalWrapper;
    const ctx = window.dash_component_api.useDashContext();
    componentPath = componentPath ?? ctx.componentPath;
    // We use the raw path here since it's up one level from
    // the tabs child.
    const isLoading = ctx.useLoading({rawPath: componentPath});
    const tabStyle = {
        ...style,
        ...(disabled ? disabled_style : {}),
        ...(selected ? selected_style : {}),
    };

    const tabClassNames = [
        'tab',
        className,
        disabled ? 'tab--disabled' : null,
        disabled ? disabled_className : null,
        selected ? 'tab--selected' : null,
        selected ? selected_className : null,
    ].filter(Boolean);

    let labelDisplay;
    if (typeof label === 'object') {
        labelDisplay = (
            <ExternalWrapper
                component={label}
                componentPath={[...componentPath, 0]}
            />
        );
    } else {
        labelDisplay = <span>{label}</span>;
    }

    return (
        <div
            data-dash-is-loading={isLoading}
            className={tabClassNames.join(' ')}
            id={id}
            style={tabStyle}
            onClick={() => {
                if (!disabled) {
                    selectHandler({value});
                }
            }}
        >
            {labelDisplay}
        </div>
    );
};

/**
 * A Dash component that lets you render pages with tabs - the Tabs component's children
 * can be dcc.Tab components, which can hold a label that will be displayed as a tab, and can in turn hold
 * children components that will be that tab's content.
 */
function Tabs({
    // eslint-disable-next-line no-magic-numbers
    mobile_breakpoint = 800,
    colors = {
        border: 'var(--Dash-Stroke-Weak)',
        primary: 'var(--Dash-Fill-Interactive-Strong)',
        background: 'var(--Dash-Fill-Weak)',
    },
    vertical = false,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persisted_props = [PersistedProps.value],
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    persistence_type = PersistenceTypes.local,
    children,
    ...props
}: TabsProps) {
    const initializedRef = useRef(false);
    const [isAboveBreakpoint, setIsAboveBreakpoint] = useState(false);

    const parseChildrenToArray = useCallback((): DashComponent[] => {
        if (!children) {
            return [];
        }
        if (children instanceof Array) {
            return children;
        }
        return [children];
    }, [children]);

    const valueOrDefault = () => {
        if (has('value', props)) {
            return props.value;
        }
        const children = parseChildrenToArray();
        if (children && children.length && children[0].props.componentPath) {
            const firstChildren = window.dash_component_api.getLayout([
                ...children[0].props.componentPath,
                'props',
                'value',
            ]);
            return firstChildren || 'tab-1';
        }
        return 'tab-1';
    };

    // Initialize value on mount if not set
    useEffect(() => {
        if (!initializedRef.current && !has('value', props)) {
            props.setProps({
                value: valueOrDefault(),
            });
            initializedRef.current = true;
        }
    }, []);

    // Setup matchMedia for responsive breakpoint
    useEffect(() => {
        const mediaQuery = window.matchMedia(
            `(min-width: ${mobile_breakpoint}px)`
        );

        // Set initial value
        setIsAboveBreakpoint(mediaQuery.matches);

        // Listen for changes
        const handler = (e: MediaQueryListEvent) =>
            setIsAboveBreakpoint(e.matches);
        mediaQuery.addEventListener('change', handler);

        return () => mediaQuery.removeEventListener('change', handler);
    }, [mobile_breakpoint]);

    let EnhancedTabs: JSX.Element[];
    let selectedTab;

    const value = valueOrDefault();

    if (children) {
        const children = parseChildrenToArray();

        EnhancedTabs = children.map((child, index) => {
            // TODO: handle components that are not dcc.Tab components (throw error)
            // enhance Tab components coming from Dash (as dcc.Tab) with methods needed for handling logic
            let childProps: Omit<TabProps, 'setProps'>;

            if (React.isValidElement(child) && child.props.componentPath) {
                childProps = window.dash_component_api.getLayout([
                    ...child.props.componentPath,
                    'props',
                ]);
            } else {
                // In case the selected tab is a string.
                childProps = {};
            }

            if (!childProps.value) {
                childProps = {...childProps, value: `tab-${index + 1}`};
            }

            // check if this child/Tab is currently selected
            if (childProps.value === value) {
                selectedTab = child;
            }

            const style = childProps.style ?? {};
            if (typeof childProps.width === 'number') {
                style.width = `${childProps.width}px`;
                style.flex = 'none';
            } else if (typeof childProps.width === 'string') {
                style.width = childProps.width;
                style.flex = 'none';
            }

            return (
                <EnhancedTab
                    key={index}
                    id={childProps.id}
                    label={childProps.label}
                    selected={value === childProps.value}
                    setProps={props.setProps}
                    className={childProps.className}
                    style={style}
                    selected_className={childProps.selected_className}
                    selected_style={childProps.selected_style}
                    value={childProps.value}
                    disabled={childProps.disabled}
                    disabled_style={childProps.disabled_style}
                    disabled_className={childProps.disabled_className}
                    componentPath={child.props.componentPath}
                />
            );
        });
    }

    const selectedTabContent = !isNil(selectedTab) ? selectedTab : '';

    const tabContainerClassNames = [
        'tab-container',
        vertical ? 'tab-container--vert' : null,
        props.className,
    ].filter(Boolean);

    const tabContentClassNames = [
        'tab-content',
        vertical ? 'tab-content--vert' : null,
        props.content_className,
    ].filter(Boolean);

    const tabParentClassNames = [
        'tab-parent',
        vertical ? ' tab-parent--vert' : null,
        isAboveBreakpoint ? ' tab-parent--above-breakpoint' : null,
        props.parent_className,
    ].filter(Boolean);

    // Set CSS variables for dynamic styling
    const cssVars = {
        '--tabs-border': colors.border,
        '--tabs-primary': colors.primary,
        '--tabs-background': colors.background,
    } as const;

    return (
        <LoadingElement>
            {loadingProps => (
                <div
                    className={tabParentClassNames.join(' ')}
                    style={{...cssVars, ...props.parent_style}}
                    id={props.id ? `${props.id}-parent` : undefined}
                    {...loadingProps}
                >
                    <div
                        className={tabContainerClassNames.join(' ')}
                        style={props.style}
                        id={props.id}
                    >
                        {EnhancedTabs}
                    </div>
                    <div
                        className={tabContentClassNames.join(' ')}
                        style={props.content_style}
                    >
                        {selectedTabContent || ''}
                    </div>
                </div>
            )}
        </LoadingElement>
    );
}

Tabs.dashPersistence = true;
Tabs.dashChildrenUpdate = true;

export default Tabs;
