'use strict';

/**
 * Generates React components from a newline-separated list of HTML elements.
 */

const fs = require('fs');
const path = require('path');

const srcPath = '../src/components';
const attributesPath = './data/attributes.json';

const PROP_TYPES = {
    _default: 'string',
    style: 'object'
};

function bail(message) {
    console.error('Error: ' + message);
    process.exit(1);
}

function upperCase(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function nameComponent(elementName) {
    const reservedWords = {
        'object': 'ObjectEl',
        'map': 'MapEl'
    };

    return reservedWords[elementName] || upperCase(elementName);
}

function generatePropTypes(element, attributes) {
    const elements = attributes.elements;
    // Always add the list of global attributes.
    const supportedAttributes = elements[element] ?
        elements[element].concat(elements.Globalattribute) :
        elements.Globalattribute;
    const numAttributes = supportedAttributes.length;

    return supportedAttributes.reduce((propTypes, attributeName, index) => {
        const attribute = attributes.attributes[attributeName];
        const propType = PROP_TYPES[attributeName] || PROP_TYPES._default;

        return propTypes + `

    /**
     *${attribute.description ? ' ' + attribute.description : ''}
     */
    '${attributeName}': PropTypes.${propType}${index < numAttributes - 1 ? ',' : ''}`;
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
        const componentName = nameComponent(element);
        const Component = generateComponent(componentName, element, attributes);

        componentMap[componentName] = Component;

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
