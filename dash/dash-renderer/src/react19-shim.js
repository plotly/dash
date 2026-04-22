/**
 * React 19 compatibility shim
 *
 * Provides compatibility for components bundled with older React versions
 * when running with React 19:
 *
 * 1. ReactCurrentOwner stub - React 19 removed this from internals but some
 *    libraries still access it.
 *
 * 2. Global jsx-runtime - Provides jsx/jsxs functions using the current React
 *    version's createElement, ensuring element format compatibility.
 *
 * Must be imported before any component code.
 */
(function () {
    if (typeof window.React === 'undefined') {
        return;
    }

    var React = window.React;

    // Provide ReactCurrentOwner stub for React 19
    var internals = React.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED;
    if (!internals) {
        React.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED = {
            ReactCurrentOwner: {current: null},
            ReactCurrentDispatcher: {current: null},
            ReactCurrentBatchConfig: {transition: null}
        };
    } else if (!internals.ReactCurrentOwner) {
        internals.ReactCurrentOwner = {current: null};
    }

    // Provide global jsx-runtime that uses current React version
    // This ensures elements are created in the correct format for the loaded React
    function jsx(type, config, maybeKey) {
        var props = {};
        var children = null;

        // Copy props, extracting children and special props
        if (config != null) {
            // Handle key - include in props for createElement
            if (config.key !== undefined) {
                props.key = '' + config.key;
            }

            for (var propName in config) {
                if (
                    Object.prototype.hasOwnProperty.call(config, propName) &&
                    propName !== 'key' &&
                    propName !== '__self' &&
                    propName !== '__source'
                ) {
                    if (propName === 'children') {
                        children = config[propName];
                    } else {
                        props[propName] = config[propName];
                    }
                }
            }
        }

        // Handle key passed as third argument (overrides config.key)
        if (maybeKey !== undefined) {
            props.key = '' + maybeKey;
        }

        // Call createElement with children as separate arguments
        // Only pass children if they exist and are meaningful
        if (children !== null && children !== undefined) {
            if (Array.isArray(children)) {
                return React.createElement.apply(
                    React,
                    [type, props].concat(children)
                );
            }
            return React.createElement(type, props, children);
        }
        return React.createElement(type, props);
    }

    window.ReactJSXRuntime = {
        jsx: jsx,
        jsxs: jsx, // jsxs is same as jsx but for static children
        Fragment: React.Fragment
    };
})();
