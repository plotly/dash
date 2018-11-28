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
        const {className, style, id, href} = this.props;
        /*
         * ideally, we would use cloneElement however
         * that doesn't work with dash's recursive
         * renderTree implementation for some reason
         */
        return (
            <a
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
    href: PropTypes.string,
    refresh: PropTypes.bool,
    className: PropTypes.string,
    style: PropTypes.object,
    id: PropTypes.string,
    children: PropTypes.node,
};

Link.defaultProps = {
    refresh: false,
};
