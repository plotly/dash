const fs = require('fs');
const glob = require('glob');
const path = require('path');

function filterProps(props) {
    let clone = Object.assign({}, props);
    delete clone.setProps;

    return clone;
}

function filterPropsNoChildren(props) {
    let clone = Object.assign({}, props);
    delete clone.setProps;
    delete clone.children;

    return clone;
}

function configFileExists(recipe, filepath) {
    return fs.existsSync(path.join(process.cwd(), '.dcg', recipe, filepath));
}

function recipeFileExists(recipePath, filepath) {
    return fs.existsSync(path.join(path.dirname(recipePath), filepath));
}

function sourceFileExists(filepath) {
    return fs.existsSync(path.join(process.cwd(), filepath));
}


function readConfigFile(recipe, filepath) {
    return fs.readFileSync(path.join(process.cwd(), '.dcg', recipe, filepath), 'utf8');
}

function readRecipeFile(recipePath, filepath) {
    return fs.readFileSync(path.join(path.dirname(recipePath), filepath), 'utf8');
}

function readSourceFile(filepath) {
    return fs.readFileSync(path.join(process.cwd(), filepath), 'utf8');
}

function getSourceFiles(filepath) {
    return sourceFileExists(filepath) ?
        glob.sync(path.join(process.cwd(), filepath, '**/*'), {}).map(p => path.relative(process.cwd(), p)) :
        [];
}

module.exports = (recipe, recipePath) => ({
    filterProps,
    filterPropsNoChildren,
    getSourceFiles,
    readConfigFile: readConfigFile.bind(undefined, recipe),
    readRecipeFile: readRecipeFile.bind(undefined, recipePath),
    readSourceFile,
    configFileExists: configFileExists.bind(undefined, recipe),
    recipeFileExists: recipeFileExists.bind(undefined, recipePath),
    sourceFileExists
});