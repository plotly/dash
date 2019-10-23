const fs = require('fs');

function getFingerprint() {
    const package = fs.readFileSync('./package.json');
    const packageJson = JSON.parse(package);

    const timestamp = Math.round(Date.now() / 1000);
    const version = packageJson.version.replace(/[.]/g, '_');

    return `"v${version}m${timestamp}"`;
}

const resolveImportSource = () => `\
Object.defineProperty(__webpack_require__, 'p', {
    get: (function () {
        let script = document.currentScript;
        if (!script) {
            /* Shim for IE11 and below */
            /* Do not take into account async scripts and inline scripts */
            const scripts = Array.from(document.getElementsByTagName('script')).filter(function(s) { return !s.async && !s.text && !s.textContent; });
            script = scripts.slice(-1)[0];
        }

        var url = script.src.split('/').slice(0, -1).join('/') + '/';

        return function() {
            return url;
        };
    })()
});

const __jsonpScriptSrc__ = jsonpScriptSrc;
jsonpScriptSrc = function(chunkId) {
    const srcFragments = __jsonpScriptSrc__(chunkId).split('.');
    srcFragments.splice(-1, 0, ${getFingerprint()});

    return srcFragments.join('.');
}
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
