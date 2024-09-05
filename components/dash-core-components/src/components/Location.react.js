import {Component} from 'react';
import PropTypes from 'prop-types';
import {type} from 'ramda';

import {History} from '@plotly/dash-component-plugins';

/**
 * Update and track the current window.location object through the window.history state.
 * Use in conjunction with the `dash_core_components.Link` component to make apps with multiple pages.
 */
export default class Location extends Component {
    constructor(props) {
        super(props);
        this.updateLocation = this.updateLocation.bind(this);
        this.onLocationChange = this.onLocationChange.bind(this);
    }

    updateLocation(props) {
        const {hash, href, pathname, refresh, search, setProps} = props;

        // Keep track of props relating to window.location that may need to be updated via setProps
        const propsToSet = {};

        /**
         * Check if the field exists in props. If the prop with "fieldName" is not defined,
         * then it was not set by the user and needs to be equal to the value in window.location.
         * This only happens on page load (since props will no longer be undefined after componentDidMount).
         *
         * @param {string} fieldName
         *  The name of the prop in window.location and in the component's prop
         *
         * @returns {boolean}
         *  Returns true if the prop with fieldName is different and the window state needs to be updated
         */
        const checkExistsUpdateWindowLocation = fieldName => {
            const propVal = props[fieldName];

            if (
                (type(propVal) === 'Undefined' || propVal === null) &&
                type(window.location[fieldName]) !== 'Undefined'
            ) {
                // propVal is undefined or null, but window.location has this fieldName defined
                propsToSet[fieldName] = window.location[fieldName];
            } else if (propVal !== window.location[fieldName]) {
                // Prop has changed?
                if (refresh === true) {
                    // Refresh the page?
                    window.location[fieldName] = propVal;
                } else if (this.props[fieldName] !== propVal) {
                    // If this prop has changed, need to setProps
                    propsToSet[fieldName] = propVal;
                    // This (`${fieldName}`: propVal) needs to be pushed in the window.history
                    return true;
                }
            }
            // This (`${fieldName}`: propVal) DOES NOT need to be pushed in the window.history
            return false;
        };

        // Check if the prop value needs to be updated (note that this mutates propsToSet)
        const pathnameUpdated = checkExistsUpdateWindowLocation('pathname');
        const hrefUpdated = checkExistsUpdateWindowLocation('href');
        const hashUpdated = checkExistsUpdateWindowLocation('hash');
        const searchUpdated = checkExistsUpdateWindowLocation('search');

        // propsToSet has been updated -- batch update to Dash
        if (Object.keys(propsToSet).length > 0) {
            setProps(propsToSet);
        }

        // Special case -- overrides everything!
        if (hrefUpdated) {
            window.history.pushState({}, '', href);
            if (refresh === 'callback-nav') {
                window.dispatchEvent(new CustomEvent('_dashprivate_pushstate'));
            }
        } else if (pathnameUpdated || hashUpdated || searchUpdated) {
            // Otherwise, we can mash everything together
            const searchVal = type(search) !== 'Undefined' ? search : '';
            const hashVal = type(hash) !== 'Undefined' ? hash : '';
            window.history.pushState(
                {},
                '',
                `${pathname}${searchVal}${hashVal}`
            );
            if (refresh === 'callback-nav') {
                window.dispatchEvent(new CustomEvent('_dashprivate_pushstate'));
            }
        }
    }

    onLocationChange() {
        const {setProps} = this.props;
        const propsToChange = {};

        if (this.props.pathname !== window.location.pathname) {
            propsToChange.pathname = window.location.pathname;
        }
        if (this.props.href !== window.location.href) {
            propsToChange.href = window.location.href;
        }
        if (this.props.hash !== window.location.hash) {
            propsToChange.hash = window.location.hash;
        }
        if (this.props.search !== window.location.search) {
            propsToChange.search = window.location.search;
        }

        setProps(propsToChange);

        History.dispatchChangeEvent();
    }

    componentDidMount() {
        window.addEventListener('popstate', this.onLocationChange);

        window.addEventListener(
            '_dashprivate_pushstate',
            this.onLocationChange
        );
        this.updateLocation(this.props);
    }

    componentWillUnmount() {
        window.removeEventListener('popstate', this.onLocationChange);
        window.removeEventListener(
            '_dashprivate_pushstate',
            this.onLocationChange
        );
    }

    UNSAFE_componentWillReceiveProps(nextProps) {
        this.updateLocation(nextProps);
    }

    render() {
        return null;
    }
}

Location.propTypes = {
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    id: PropTypes.string.isRequired,

    /** pathname in window.location - e.g., "/my/full/pathname" */
    pathname: PropTypes.string,
    /** search in window.location - e.g., "?myargument=1" */
    search: PropTypes.string,
    /** hash in window.location - e.g., "#myhash" */
    hash: PropTypes.string,
    /** href in window.location - e.g., "/my/full/pathname?myargument=1#myhash" */
    href: PropTypes.string,

    /**
     * Use `True` to navigate outside the Dash app or to manually refresh a page.
     * Use `False` if the same callback that updates the Location component is also
     * updating the page content - typically used in multi-page apps that do not use Pages.
     * Use 'callback-nav' if you are updating the URL in a callback, or a different
     * callback will respond to the new Location with updated content. This is
     * typical with multi-page apps that use Pages. This will allow for
     * navigating to a new page without refreshing the page.
     */
    refresh: PropTypes.oneOfType([
        PropTypes.oneOf(['callback-nav']),
        PropTypes.bool,
    ]),

    /**
     * Dash-assigned callback that gets fired when the value changes.
     */
    setProps: PropTypes.func,
};

Location.defaultProps = {
    refresh: true,
};
