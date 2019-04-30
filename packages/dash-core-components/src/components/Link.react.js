/* global window:true */

import PropTypes from 'prop-types';

import React, {Component} from 'react';

/*
 * event polyfill for IE
 * https://developer.mozilla.org/en-US/docs/Web/API/CustomEvent/CustomEvent
 */
function CustomEvent(event, params) {
    // eslint-disable-next-line no-param-reassign
    params = params || {
        bubbles: false,
        cancelable: false,
        // eslint-disable-next-line no-undefined
        detail: undefined,
    };
    const evt = document.createEvent('CustomEvent');
    evt.initCustomEvent(
        event,
        params.bubbles,
        params.cancelable,
        params.detail
    );
    return evt;
}
CustomEvent.prototype = window.Event.prototype;

/**
 * Link allows you to create a clickable link within a multi-page app.
 *
 * For links with destinations outside the current app, `html.A` is a better
 * component to use.
 */
export default class Link extends Component {
    constructor(props) {
        super(props);
        this.updateLocation = this.updateLocation.bind(this);
    }

    updateLocation(e) {
        // prevent anchor from updating location
        e.preventDefault();
        const {href, refresh} = this.props;
        if (refresh) {
            window.location.pathname = href;
        } else {
            window.history.pushState({}, '', href);
            window.dispatchEvent(new CustomEvent('onpushstate'));
        }
        // scroll back to top
        window.scrollTo(0, 0);
    }

    render() {
        const {className, style, id, href, loading_state} = this.props;
        /*
         * ideally, we would use cloneElement however
         * that doesn't work with dash's recursive
         * renderTree implementation for some reason
         */
        return (
            <a
                data-dash-is-loading={
                    (loading_state && loading_state.is_loading) || undefined
                }
                id={id}
                className={className}
                style={style}
                href={href}
                onClick={e => this.updateLocation(e)}
            >
                {this.props.children}
            </a>
        );
    }
}

Link.propTypes = {
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string,
    /**
     * The URL of a linked resource.
     */
    href: PropTypes.string,
    /**
     * Controls whether or not the page will refresh when the link is clicked
     */
    refresh: PropTypes.bool,
    /**
     * Often used with CSS to style elements with common properties.
     */
    className: PropTypes.string,
    /**
     * Defines CSS styles which will override styles previously set.
     */
    style: PropTypes.object,
    /**
     * The children of this component
     */
    children: PropTypes.node,
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
};

Link.defaultProps = {
    refresh: false,
};
