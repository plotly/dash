const fs = require('fs');

const package = JSON.parse(fs.readFileSync('package.json'));

const plotlyJsVersion = (package.dependencies && package.dependencies['plotly.js']) ||
    (package.devDependencies && package.devDependencies['plotly.js']);

fs.copyFile('node_modules/plotly.js/dist/plotly.min.js', `dash_core_components/plotly-${plotlyJsVersion}.min.js`, err => {
    if (err) {
        throw err;
    }

    console.log('copied plotly.js', plotlyJsVersion);
});