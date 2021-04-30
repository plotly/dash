const {dest, parallel, src} = require('gulp');
const fs = require('fs-extra');
const log = require('fancy-log')
const print = require('gulp-print').default;
const replace = require('gulp-replace');
const packageJSON = require('./package.json')

// Copy dash-renderer artifacts to dash directory
function copyRendererArtifacts() {
    if (fs.existsSync('dash_renderer/')) {
        return src('dash_renderer/*.js')
        .pipe(print())
        .pipe(dest('../dash/deps', { overwrite: true }))
    }

    return log(`dash_renderer directory does not exist.
        Please build the dash-renderer package before running this task.`)
}


// Update js_dist_dependencies in dash directory
function updateRendererVersions() {
    if (fs.existsSync('dash_renderer/')) {
        const dependencyVersions = {
            'dash_renderer': packageJSON.version,
            'polyfill': packageJSON.dependencies['@babel/polyfill'],
            'react': packageJSON.dependencies.react,
            'react_dom': packageJSON.dependencies['react-dom'],
            'prop_types': packageJSON.dependencies['prop-types']
        }
        return src('../dash/_dash_renderer.py')
        .pipe(replace(/\{(.+?)\}/s, JSON.stringify(dependencyVersions, null, '    ')))
        .pipe(dest('../dash/', { overwrite: true }))
    }

    return log(`dash_renderer directory does not exist.
        Please build the dash-renderer package before running this task.`)
}


exports.merge_renderer = parallel(
    copyRendererArtifacts,
    updateRendererVersions
)
