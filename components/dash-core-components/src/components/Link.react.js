import PropTypes from 'prop-types';

import React, {useEffect, useMemo} from 'react';
import {isNil} from 'ramda';

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
const Link = ({refresh = false, ...props}) => {
    const {className, style, id, href, children, title, target, setProps} =
        props;
    const cleanUrl = window.dash_clientside.clean_url;
    const sanitizedUrl = useMemo(() => {
        return href ? cleanUrl(href) : undefined;
    }, [href]);

    const ctx = window.dash_component_api.useDashContext();
    const loading = ctx.useLoading();

    const updateLocation = e => {
        const hasModifiers = e.metaKey || e.shiftKey || e.altKey || e.ctrlKey;

        if (hasModifiers) {
            return;
        }
        if (target !== '_self' && !isNil(target)) {
            return;
        }
        // prevent anchor from updating location
        e.preventDefault();
        if (refresh) {
            window.location = sanitizedUrl;
        } else {
            window.history.pushState({}, '', sanitizedUrl);
            window.dispatchEvent(new CustomEvent('_dashprivate_pushstate'));
        }
        // scroll back to top
        window.scrollTo(0, 0);
    };

    useEffect(() => {
        if (sanitizedUrl && sanitizedUrl !== href) {
            setProps({
                _dash_error: new Error(`Dangerous link detected:: ${href}`),
            });
        }
    }, [href, sanitizedUrl]);

    return (
        <a
            data-dash-is-loading={loading || undefined}
            id={id}
            className={className}
            style={style}
            href={sanitizedUrl}
            onClick={updateLocation}
            title={title}
            target={target}
        >
            {isNil(children) ? sanitizedUrl : children}
        </a>
    );
};

Link.propTypes = {
    /**
     * The children of this component
     */
    children: PropTypes.node,
    /**
     * The URL of a linked resource.
     */
    href: PropTypes.string.isRequired,
    /**
     * Specifies where to open the link reference.
     */
    target: PropTypes.string,
    /**
     * Controls whether or not the page will refresh when the link is clicked
     */
    refresh: PropTypes.bool,

    /**
     * Adds the title attribute to your link, which can contain supplementary
     * information.
     */
    title: PropTypes.string,

    /**
     * Often used with CSS to style elements with common properties.
     */
    className: PropTypes.string,
    /**
     * Defines CSS styles which will override styles previously set.
     */
    style: PropTypes.object,
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string,
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
    setProps: PropTypes.func,
};

export default Link;
