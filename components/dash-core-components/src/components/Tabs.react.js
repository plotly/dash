/* eslint-disable react/prop-types */
import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {has, is, isNil} from 'ramda';

// some weird interaction btwn styled-jsx 3.4 and babel
// see https://github.com/vercel/styled-jsx/pull/716
import _JSXStyle from 'styled-jsx/style'; // eslint-disable-line no-unused-vars

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
    disabled,
    disabled_style,
    disabled_className,
    mobile_breakpoint,
    amountOfTabs,
    colors,
    vertical,
    loading_state,
}) => {
    let tabStyle = style;
    if (disabled) {
        tabStyle = {tabStyle, ...disabled_style};
    }
    if (selected) {
        tabStyle = {tabStyle, ...selected_style};
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
            data-dash-is-loading={
                (loading_state && loading_state.is_loading) || undefined
            }
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
            <style jsx>{`
                .tab {
                    display: inline-block;
                    background-color: ${colors.background};
                    border: 1px solid ${colors.border};
                    border-bottom: none;
                    padding: 20px 25px;
                    transition: background-color, color 200ms;
                    width: 100%;
                    text-align: center;
                    box-sizing: border-box;
                }
                .tab:last-of-type {
                    border-right: 1px solid ${colors.border};
                    border-bottom: 1px solid ${colors.border};
                }
                .tab:hover {
                    cursor: pointer;
                }
                .tab--selected {
                    border-top: 2px solid ${colors.primary};
                    color: black;
                    background-color: white;
                }
                .tab--selected:hover {
                    background-color: white;
                }
                .tab--disabled {
                    color: #d6d6d6;
                }

                @media screen and (min-width: ${mobile_breakpoint}px) {
                    .tab {
                        border: 1px solid ${colors.border};
                        border-right: none;
                        ${vertical
                            ? ''
                            : `width: calc(100% / ${amountOfTabs});`};
                    }
                    .tab--selected,
                    .tab:last-of-type.tab--selected {
                        border-bottom: none;
                        ${vertical
                            ? `border-left: 2px solid ${colors.primary};`
                            : `border-top: 2px solid ${colors.primary};`};
                    }
                }
            `}</style>
        </div>
    );
};

EnhancedTab.defaultProps = {
    loading_state: {
        is_loading: false,
        component_name: '',
        prop_name: '',
    },
};

/**
 * A Dash component that lets you render pages with tabs - the Tabs component's children
 * can be dcc.Tab components, which can hold a label that will be displayed as a tab, and can in turn hold
 * children components that will be that tab's content.
 */
export default class Tabs extends Component {
    constructor(props) {
        super(props);

        this.selectHandler = this.selectHandler.bind(this);
        this.parseChildrenToArray = this.parseChildrenToArray.bind(this);
        this.valueOrDefault = this.valueOrDefault.bind(this);

        if (!has('value', this.props)) {
            this.props.setProps({
                value: this.valueOrDefault(),
            });
        }
    }

    valueOrDefault() {
        if (has('value', this.props)) {
            return this.props.value;
        }
        const children = this.parseChildrenToArray();
        if (children && children[0].props.children) {
            return children[0].props.children.props.value || 'tab-1';
        }
        return 'tab-1';
    }

    parseChildrenToArray() {
        if (this.props.children && !is(Array, this.props.children)) {
            // if dcc.Tabs.children contains just one single element, it gets passed as an object
            // instead of an array - so we put in in a array ourselves!
            return [this.props.children];
        }
        return this.props.children;
    }

    selectHandler(value) {
        this.props.setProps({value: value});
    }

    render() {
        let EnhancedTabs;
        let selectedTab;

        if (this.props.children) {
            const children = this.parseChildrenToArray();

            const amountOfTabs = children.length;

            EnhancedTabs = children.map((child, index) => {
                // TODO: handle components that are not dcc.Tab components (throw error)
                // enhance Tab components coming from Dash (as dcc.Tab) with methods needed for handling logic
                let childProps;

                if (
                    // disabled is a defaultProp (so it's always set)
                    // meaning that if it's not set on child.props, the actual
                    // props we want are lying a bit deeper - which means they
                    // are coming from Dash
                    isNil(child.props.disabled) &&
                    child.props._dashprivate_layout &&
                    child.props._dashprivate_layout.props
                ) {
                    // props are coming from Dash
                    childProps = child.props._dashprivate_layout.props;
                } else {
                    // else props are coming from React (Demo.react.js, or Tabs.test.js)
                    childProps = child.props;
                }

                if (!childProps.value) {
                    childProps = {...childProps, value: `tab-${index + 1}`};
                }

                // check if this child/Tab is currently selected
                if (childProps.value === this.valueOrDefault()) {
                    selectedTab = child;
                }

                return (
                    <EnhancedTab
                        key={index}
                        id={childProps.id}
                        label={childProps.label}
                        selected={this.valueOrDefault() === childProps.value}
                        selectHandler={this.selectHandler}
                        className={childProps.className}
                        style={childProps.style}
                        selectedClassName={childProps.selected_className}
                        selected_style={childProps.selected_style}
                        value={childProps.value}
                        disabled={childProps.disabled}
                        disabled_style={childProps.disabled_style}
                        disabled_className={childProps.disabled_className}
                        mobile_breakpoint={this.props.mobile_breakpoint}
                        vertical={this.props.vertical}
                        amountOfTabs={amountOfTabs}
                        colors={this.props.colors}
                        loading_state={childProps.loading_state}
                    />
                );
            });
        }

        const selectedTabContent = !isNil(selectedTab) ? selectedTab : '';

        const tabContainerClass = this.props.vertical
            ? 'tab-container tab-container--vert'
            : 'tab-container';

        const tabContentClass = this.props.vertical
            ? 'tab-content tab-content--vert'
            : 'tab-content';

        const tabParentClass = this.props.vertical
            ? 'tab-parent tab-parent--vert'
            : 'tab-parent';

        return (
            <div
                data-dash-is-loading={
                    (this.props.loading_state &&
                        this.props.loading_state.is_loading) ||
                    undefined
                }
                className={`${tabParentClass} ${
                    this.props.parent_className || ''
                }`}
                style={this.props.parent_style}
                id={`${this.props.id}-parent`}
            >
                <div
                    className={`${tabContainerClass} ${
                        this.props.className || ''
                    }`}
                    style={this.props.style}
                    id={this.props.id}
                >
                    {EnhancedTabs}
                </div>
                <div
                    className={`${tabContentClass} ${
                        this.props.content_className || ''
                    }`}
                    style={this.props.content_style}
                >
                    {selectedTabContent || ''}
                </div>
                <style jsx>{`
                    .tab-parent {
                        display: flex;
                        flex-direction: column;
                    }
                    .tab-container {
                        display: flex;
                        flex-direction: column;
                    }
                    .tab-container--vert {
                        display: inline-flex;
                    }
                    .tab-content--vert {
                        display: inline-flex;
                        flex-direction: column;
                    }
                    @media screen and (min-width: ${this.props
                            .mobile_breakpoint}px) {
                        :global(.tab-container--vert .tab) {
                            width: auto;
                            border-right: none !important;
                            border-bottom: none !important;
                        }
                        :global(.tab-container--vert .tab:last-of-type) {
                            border-bottom: 1px solid ${this.props.colors.border} !important;
                        }
                        :global(.tab-container--vert .tab--selected) {
                            border-top: 1px solid ${this.props.colors.border};
                            border-left: 2px solid ${this.props.colors.primary};
                            border-right: none;
                        }
                        .tab-container {
                            flex-direction: row;
                        }
                        .tab-container--vert {
                            flex-direction: column;
                        }
                        .tab-parent--vert {
                            display: inline-flex;
                            flex-direction: row;
                        }
                    }
                `}</style>
            </div>
        );
    }
}

Tabs.defaultProps = {
    mobile_breakpoint: 800,
    colors: {
        border: '#d6d6d6',
        primary: '#1975FA',
        background: '#f9f9f9',
    },
    vertical: false,
    persisted_props: ['value'],
    persistence_type: 'local',
};

Tabs.propTypes = {
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string,

    /**
     * The value of the currently selected Tab
     */
    value: PropTypes.string,

    /**
     * Appends a class to the Tabs container holding the individual Tab components.
     */
    className: PropTypes.string,

    /**
     * Appends a class to the Tab content container holding the children of the Tab that is selected.
     */
    content_className: PropTypes.string,

    /**
     * Appends a class to the top-level parent container holding both the Tabs container and the content container.
     */
    parent_className: PropTypes.string,

    /**
     * Appends (inline) styles to the Tabs container holding the individual Tab components.
     */
    style: PropTypes.object,

    /**
     * Appends (inline) styles to the top-level parent container holding both the Tabs container and the content container.
     */
    parent_style: PropTypes.object,

    /**
     * Appends (inline) styles to the tab content container holding the children of the Tab that is selected.
     */
    content_style: PropTypes.object,

    /**
     * Renders the tabs vertically (on the side)
     */
    vertical: PropTypes.bool,

    /**
     * Breakpoint at which tabs are rendered full width (can be 0 if you don't want full width tabs on mobile)
     */
    mobile_breakpoint: PropTypes.number,

    /**
     * Array that holds Tab components
     */
    children: PropTypes.oneOfType([
        PropTypes.arrayOf(PropTypes.node),
        PropTypes.node,
    ]),

    /**
     * Holds the colors used by the Tabs and Tab components. If you set these, you should specify colors for all properties, so:
     * colors: {
     *    border: '#d6d6d6',
     *    primary: '#1975FA',
     *    background: '#f9f9f9'
     *  }
     */
    colors: PropTypes.exact({
        border: PropTypes.string,
        primary: PropTypes.string,
        background: PropTypes.string,
    }),

    /**
     * Object that holds the loading state object coming from dash-renderer
     */
    loading_state: PropTypes.shape({
        /**
         * Determines if the component is loading or not
         */
        is_loading: PropTypes.bool,
        /**
         * Holds which property is loading
         */
        prop_name: PropTypes.string,
        /**
         * Holds the name of the component that is loading
         */
        component_name: PropTypes.string,
    }),

    /**
     * Used to allow user interactions in this component to be persisted when
     * the component - or the page - is refreshed. If `persisted` is truthy and
     * hasn't changed from its previous value, a `value` that the user has
     * changed while using the app will keep that change, as long as
     * the new `value` also matches what was given originally.
     * Used in conjunction with `persistence_type`.
     */
    persistence: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.string,
        PropTypes.number,
    ]),

    /**
     * Properties whose user interactions will persist after refreshing the
     * component or the page. Since only `value` is allowed this prop can
     * normally be ignored.
     */
    persisted_props: PropTypes.arrayOf(PropTypes.oneOf(['value'])),

    /**
     * Where persisted user changes will be stored:
     * memory: only kept in memory, reset on page refresh.
     * local: window.localStorage, data is kept after the browser quit.
     * session: window.sessionStorage, data is cleared once the browser quit.
     */
    persistence_type: PropTypes.oneOf(['local', 'session', 'memory']),
};
