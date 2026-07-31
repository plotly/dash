// Shared webpack external for react/jsx-runtime and react/jsx-dev-runtime,
// reused by the renderer, dcc, html and table webpack configs.
//
// Newer Dash provides window.ReactJSXRuntime (see src/react-shim.js) backed by
// the React version loaded on the page; the inline fallback below rebuilds an
// equivalent runtime from window.React.createElement (and caches it on
// window.ReactJSXRuntime) so bundles built with this convention keep working on
// older Dash, which never defines the global.
//
// The jsx implementation MUST stay in sync with the one in src/react-shim.js.
const jsxRuntimeExternal = `var (window.ReactJSXRuntime || (window.ReactJSXRuntime = (function (React) {
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
        if (maybeKey !== undefined) {
            props.key = '' + maybeKey;
        }
        if (children === null || children === undefined) {
            return React.createElement(type, props);
        }
        return Array.isArray(children)
            ? React.createElement.apply(React, [type, props].concat(children))
            : React.createElement(type, props, children);
    }
    return {jsx: jsx, jsxs: jsx, jsxDEV: jsx, Fragment: React.Fragment};
})(window.React)))`;

module.exports = {jsxRuntimeExternal};
