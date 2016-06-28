'use strict';

/**
 * Generates React components from a newline-separated list of HTML elements.
 */

const fs = require('fs');
const path = require('path');

const srcPath = '../src/components';

function bail(message) {
    console.error('Error: ' + message);
    process.exit(1);
}

function upperCase(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function generateComponent(Component, element) {
    return `
import React from 'react';

const ${Component} = (props) => (
    <${element}>
        {props.children}
    </${element}>
);

export default ${Component};
    `;
}

// Get first command-line argument
const listPath = process.argv[2];

if (!listPath) {
    bail('Must specify an element list.');
}

// Read the list of elements
const list = fs
    .readFileSync(listPath, 'utf8')
    .split('\n')
    .filter(item => !!item);

// Generate an object with Component names as keys, component definitions as values
const components = list.reduce((componentMap, element) => {
    const Component = upperCase(element);
    componentMap[Component] = generateComponent(Component, element);
    return componentMap;
}, {});

let componentPath;
console.log(`Writing ${Object.keys(components).length} component files to ${srcPath}.`);
for (let Component in components) {
    componentPath = path.join(srcPath, `${Component}.react.js`);
    fs.writeFileSync(componentPath, components[Component]);
}
console.log('Done.');
