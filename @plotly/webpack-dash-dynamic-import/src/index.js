const fs = require('fs');

function getFingerprint() {
    const package = fs.readFileSync('./package.json');
    const packageJson = JSON.parse(package);

    const timestamp = Math.round(Date.now() / 1000);
    const version = packageJson.version.replace(/[.]/g, '_').replace(/[+]/g, '__');

    return `"v${version}m${timestamp}"`;
}

const resolveImportSource = () => `\
const getCurrentScript = function() {
    let script = document.currentScript;
    if (!script) {
        /* Shim for IE11 and below */
        /* Do not take into account async scripts and inline scripts */
        const scripts = Array.from(document.getElementsByTagName('script')).filter(function(s) { return !s.async && !s.text && !s.textContent; });
        script = scripts.slice(-1)[0];
    }

    return script;
};

const isLocalScript = function(script) {
    return /\\\/_dash-component-suites\\\//.test(script.src);
};

Object.defineProperty(__webpack_require__, 'p', {
    get: (function () {
        let script = getCurrentScript();

        var url = script.src.split('/').slice(0, -1).join('/') + '/';

        return function() {
            return url;
        };
    })()
});

const __jsonpScriptSrc__ = jsonpScriptSrc;
jsonpScriptSrc = function(chunkId) {
    let script = getCurrentScript();
    let isLocal = isLocalScript(script);

    let src = __jsonpScriptSrc__(chunkId);

    if(!isLocal) {
        return src;
    }

    const srcFragments = src.split('/');
    const fileFragments = srcFragments.slice(-1)[0].split('.');

    fileFragments.splice(1, 0, ${getFingerprint()});
    srcFragments.splice(-1, 1, fileFragments.join('.'))

    return srcFragments.join('/');
};
`

class WebpackDashDynamicImport {
    apply(compiler) {
        compiler.hooks.compilation.tap('WebpackDashDynamicImport', compilation => {
            compilation.mainTemplate.hooks.requireExtensions.tap('WebpackDashDynamicImport > RequireExtensions', (source, chunk, hash) => {
                return [
                    source,
                    resolveImportSource()
                ]
            });
        });
    }
}

module.exports = WebpackDashDynamicImport;
