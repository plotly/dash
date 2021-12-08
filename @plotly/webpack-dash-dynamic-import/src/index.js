const fs = require('fs');

function getFingerprint() {
    const package = fs.readFileSync('./package.json');
    const packageJson = JSON.parse(package);

    const timestamp = Math.round(Date.now() / 1000);
    const version = packageJson.version.replace(/[^\w-]/g, '_');

    return `"v${version}m${timestamp}"`;
}

/**
 * This code is injected as-is in the webpack artifact and must be ES5 compatible to work in all scenarios.
 * This will not get transpiled.
 */
const resolveImportSource = () => `\
var getCurrentScript = function() {
    var script = document.currentScript;
    if (!script) {
        /* Shim for IE11 and below */
        /* Do not take into account async scripts and inline scripts */

        var doc_scripts = document.getElementsByTagName('script');
        var scripts = [];

        for (var i = 0; i < doc_scripts.length; i++) {
            scripts.push(doc_scripts[i]);
        }

        scripts = scripts.filter(function(s) { return !s.async && !s.text && !s.textContent; });
        script = scripts.slice(-1)[0];
    }

    return script;
};

var isLocalScript = function(script) {
    return /\\\/_dash-component-suites\\\//.test(script.src);
};

Object.defineProperty(__webpack_require__, 'p', {
    get: (function () {
        var script = getCurrentScript();

        var url = script.src.split('/').slice(0, -1).join('/') + '/';

        return function() {
            return url;
        };
    })()
});

if (typeof jsonpScriptSrc !== 'undefined') {
    var __jsonpScriptSrc__ = jsonpScriptSrc;
    jsonpScriptSrc = function(chunkId) {
        var script = getCurrentScript();
        var isLocal = isLocalScript(script);

        var src = __jsonpScriptSrc__(chunkId);

        if(!isLocal) {
            return src;
        }

        var srcFragments = src.split('/');
        var fileFragments = srcFragments.slice(-1)[0].split('.');

        fileFragments.splice(1, 0, ${getFingerprint()});
        srcFragments.splice(-1, 1, fileFragments.join('.'))

        return srcFragments.join('/');
    };
}
`

class WebpackDashDynamicImport {
    apply(compiler) {
        compiler.hooks.compilation.tap('WebpackDashDynamicImport', compilation => {
            compilation.mainTemplate.hooks.requireExtensions.tap('WebpackDashDynamicImport > RequireExtensions', (source, chunk, hash) => {
                // Prevent CSS chunks from having JS appended to them
                if (chunk.name === 'mini-css-extract-plugin') {
                    return source;
                }
                return source + resolveImportSource();
            });
        });
    }
}

module.exports = WebpackDashDynamicImport;
