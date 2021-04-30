const {dest, parallel, src} = require('gulp');
const fs = require('fs-extra');
const log = require('fancy-log')
const print = require('gulp-print').default;
const replace = require('gulp-replace');

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
        let rendererDeps = fs.readFileSync('dash_renderer/__init__.py').toString().split('\n')
        rendererDeps = rendererDeps.slice(4).join('\n')
        return src('../dash/_dash_renderer.py')
        .pipe(replace(/.*/s, rendererDeps))
        .pipe(dest('../dash/', { overwrite: true }))
    }

    return log(`dash_renderer directory does not exist.
        Please build the dash-renderer package before running this task.`)
}

exports.merge_renderer = parallel(
    copyRendererArtifacts,
    updateRendererVersions
)