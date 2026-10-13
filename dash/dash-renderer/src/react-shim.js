/**
 * React compatibility shim
 *
 * Provides compatibility for component packages bundled against other React
 * versions than the one loaded on the page:
 *
 * 1. ReactCurrentOwner stub - React 19 removed
 *    __SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED but many component
 *    libraries built against React <=18 still access it at load time.
 *
 * 2. Legacy element symbol - React 19 changed the element $$typeof symbol
 *    from 'react.element' to 'react.transitional.element' and throws
 *    error #525 on elements carrying the old symbol. Libraries that
 *    pre-bundled a React <=18 copy of react/jsx-runtime create such
 *    elements. This shim runs after React (whose own symbols are already
 *    computed) but before component packages, so redirecting
 *    Symbol.for('react.element') to the transitional symbol makes those
 *    bundled runtimes produce elements the loaded React 19 accepts.
 *
 * 3. Global jsx-runtime (window.ReactJSXRuntime) - components externalize
 *    react/jsx-runtime and react/jsx-dev-runtime to this global, so their
 *    elements are always created by the React version loaded on the page.
 *
 * This file is loaded standalone right after react/react-dom, before any
 * component package. It is also imported at the top of the dash-renderer
 * bundle, and the webpack configs (renderer, dcc, html, table) embed a copy
 * of the jsx fallback in their react/jsx-runtime external so bundles built
 * with that convention keep working on older Dash, which never defines
 * window.ReactJSXRuntime. It must stay idempotent, and the jsx implementation
 * must stay in sync with the fallback in those configs.
 */
(function () {
    if (typeof window === 'undefined' || typeof window.React === 'undefined') {
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

    // Redirect the legacy element symbol for code loaded after this shim
    var reactMajor = parseInt((React.version || '').split('.')[0], 10);
    if (
        reactMajor >= 19 &&
        Symbol.for('react.element') !== Symbol.for('react.transitional.element')
    ) {
        var elementSymbol = Symbol.for('react.transitional.element');
        var originalSymbolFor = Symbol.for;
        Symbol.for = function (key) {
            if (key === 'react.element') {
                return elementSymbol;
            }
            return originalSymbolFor.apply(Symbol, arguments);
        };
    }

    if (window.ReactJSXRuntime) {
        return;
    }

    // Provide a global jsx-runtime backed by the loaded React's createElement
    // so elements are created in the format the loaded React expects.
    function jsx(type, config, maybeKey) {
        var props = {};
        var children = null;

        if (config != null) {
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

        // Key passed as third argument overrides config.key
        if (maybeKey !== undefined) {
            props.key = '' + maybeKey;
        }

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
        jsxs: jsx, // jsxs is jsx with static children
        jsxDEV: jsx, // jsx-dev-runtime; extra dev-only arguments are ignored
        Fragment: React.Fragment
    };
})();
