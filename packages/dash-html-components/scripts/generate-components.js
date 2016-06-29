'use strict';

/**
 * Generates React components from a newline-separated list of HTML elements.
 */

const fs = require('fs');
const path = require('path');

const srcPath = '../src/components';
const attributesPath = './data/attributes.json';

function bail(message) {
    console.error('Error: ' + message);
    process.exit(1);
}

function upperCase(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function generatePropTypes(element, attributes) {
    const supportedAttributes = attributes.elements[element] || attributes.elements.Globalattribute;
    const numAttributes = supportedAttributes.length;

    return supportedAttributes.reduce((propTypes, attributeName, index) => {
        const attribute = attributes.attributes[attributeName];

        return propTypes + `

    /**
     * ${attribute.description}
     */
    '${attributeName}': PropTypes.string${index < numAttributes - 1 ? ',' : ''}
        `;
    }, '');
}

function generateComponent(Component, element, attributes) {
    const propTypes = generatePropTypes(element, attributes);

    return `
import React, {PropTypes} from 'react';

const ${Component} = (props) => (
    <${element} {...props}>
        {props.children}
    </${element}>
);

${Component}.propTypes = {${propTypes}
};

export default ${Component};
    `;
}

/**
 * Generate an object with Component names as keys, component definitions as
 * values
 */
function generateComponents(list, attributes) {
    return list.reduce((componentMap, element) => {
        const Component = upperCase(element);
        componentMap[Component] = generateComponent(Component, element, attributes);
        return componentMap;
    }, {});
}

/**
 * Writes component definitions to disk.
 */
function writeComponents(components, destination) {
    console.log(`Writing ${Object.keys(components).length} component files to ${srcPath}.`);
    let componentPath;
    for (let Component in components) {
        componentPath = path.join(destination, `${Component}.react.js`);
        fs.writeFileSync(componentPath, components[Component]);
    }
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

// Get the mapping of attributes to elements
const attributes = JSON.parse(fs.readFileSync(attributesPath, 'utf-8'));

const components = generateComponents(list, attributes);

writeComponents(components, srcPath);

console.log('Done.');
