import React, {useEffect, useRef, useState} from 'react';
import {has, is, isNil} from 'ramda';

import LoadingElement from '../utils/_LoadingElement';
import {DashComponent} from '@dash-renderer/types/component';
import './css/tabs.css';

interface EnhancedTabProps {
    id?: string;
    label?: string | DashComponent[];
    selected: boolean;
    className?: string;
    style?: React.CSSProperties;
    selectedClassName?: string;
    selected_style?: React.CSSProperties;
    selectHandler: (value: string) => void;
    value: string;
    disabled?: boolean;
    disabled_style?: React.CSSProperties;
    disabled_className?: string;
    componentPath: string[];
}
import {PersistedProps, PersistenceTypes, TabsProps} from '../types';

// EnhancedTab is defined here instead of in Tab.react.js because if exported there,
// it will mess up the Python imports and metadata.json
const EnhancedTab = ({
    id,
    label,
    selected,
    className,
    style,
    selectedClassName,
    selected_style,
    selectHandler,
    value,
    disabled = false,
    disabled_style = {color: '#d6d6d6'},
    disabled_className,
    componentPath,
}: EnhancedTabProps) => {
    const ctx = window.dash_component_api.useDashContext();
    // We use the raw path here since it's up one level from
    // the tabs child.
    const isLoading = ctx.useLoading({rawPath: !!componentPath});

    let tabStyle = style;
    if (disabled) {
        tabStyle = {...tabStyle, ...disabled_style};
    }
    if (selected) {
        tabStyle = {...tabStyle, ...selected_style};
    }
    let tabClassName = `tab ${className || ''}`;
    if (disabled) {
        tabClassName += ` tab--disabled ${disabled_className || ''}`;
    }
    if (selected) {
        tabClassName += ` tab--selected ${selectedClassName || ''}`;
    }
    let labelDisplay;
    if (is(Array, label)) {
        // label is an array, so it has children that we want to render
        labelDisplay = label[0].props.children;
    } else {
        // else it is a string, so we just want to render that
        labelDisplay = label;
    }
    return (
        <div
            data-dash-is-loading={isLoading}
            className={tabClassName}
            id={id}
            style={tabStyle}
            onClick={() => {
                if (!disabled) {
                    selectHandler(value);
                }
            }}
        >
            <span>{labelDisplay}</span>
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
    ...props
}: TabsProps) {
    const initializedRef = useRef(false);
    const [isAboveBreakpoint, setIsAboveBreakpoint] = useState(false);

    const parseChildrenToArray = () => {
        if (props.children && !is(Array, props.children)) {
            // if dcc.Tabs.children contains just one single element, it gets passed as an object
            // instead of an array - so we put it in an array ourselves!
            return [props.children];
        }
        return props.children ?? [];
    };

    const valueOrDefault = () => {
        if (has('value', props)) {
            return props.value;
        }
        const children = parseChildrenToArray();
        if (children && children.length) {
            const firstChildren = window.dash_component_api.getLayout([
                ...children[0].props.componentPath,
                'props',
                'value',
            ]);
            return firstChildren || 'tab-1';
        }
        return 'tab-1';
    };

    const selectHandler = (value: string) => {
        props.setProps({value: value});
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

    if (props.children) {
        const children = parseChildrenToArray();

        EnhancedTabs = children.map((child, index) => {
            // TODO: handle components that are not dcc.Tab components (throw error)
            // enhance Tab components coming from Dash (as dcc.Tab) with methods needed for handling logic
            let childProps;

            if (React.isValidElement(child)) {
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

            return (
                <EnhancedTab
                    key={index}
                    id={childProps.id}
                    label={childProps.label}
                    selected={value === childProps.value}
                    selectHandler={selectHandler}
                    className={childProps.className}
                    style={childProps.style}
                    selectedClassName={childProps.selected_className}
                    selected_style={childProps.selected_style}
                    value={childProps.value}
                    disabled={childProps.disabled}
                    disabled_style={childProps.disabled_style}
                    disabled_className={childProps.disabled_className}
                    componentPath={child.componentPath}
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
        '--tabs-width': `calc(100% / ${parseChildrenToArray().length})`,
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
