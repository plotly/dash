const fs = require('fs');
const path = require('path');

function filterProps(props) {
    let clone = Object.assign({}, props);
    delete clone.setProps;

    return clone;
}

function readFile(recipe, filepath) {
    return fs.readFileSync(path.join(process.cwd(), '.dcg', recipe, filepath), 'utf8');
}

function readRecipeFile(recipePath, filepath) {
    return fs.readFileSync(path.join(path.dirname(recipePath), filepath), 'utf8');
}

module.exports = (recipe, recipePath) => ({
    filterProps,
    readFile: readFile.bind(undefined, recipe),
    readRecipeFile: readRecipeFile.bind(undefined, recipePath)
});