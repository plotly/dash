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

    return `
    /**
     * The ID of this component, used to identify dash components
     * in callbacks. The ID needs to be unique across all of the
     * components in an app.
     */
    'id': PropTypes.string,

    /**
     * The children of this component
     */
    'children': PropTypes.node,

    /**
     * An integer that represents the number of times
     * that this element has been clicked on.
     */
    'n_clicks': PropTypes.integer,

    /**
     * An integer that represents the time (in ms since 1970)
     * at which n_clicks changed. This can be used to tell
     * which button was changed most recently.
     */
    'n_clicks_timestamp': PropTypes.integer,

    /**
     * A unique identifier for the component, used to improve
     * performance by React.js while rendering components
     * See https://reactjs.org/docs/lists-and-keys.html for more info
     */
    'key': PropTypes.string,

    /**
     * The ARIA role attribute
     */
    'role': PropTypes.string,

    /**
     * A wildcard data attribute
     */
    'data-*': PropTypes.string,

    /**
     * A wildcard aria attribute
     */
    'aria-*': PropTypes.string,
    ` +

    supportedAttributes.reduce((propTypes, attributeName) => {
        const attribute = attributes.attributes[attributeName];
        const propType = PROP_TYPES[attributeName] || PROP_TYPES._default;
        if (attributeName === 'id') {
            return propTypes;
        }
        return propTypes + `

    /**
     *${attribute.description ? ' ' + attribute.description : ''}
     */
    '${attributeName}': PropTypes.${propType},`;
    }, '') + `

    /**
     * A callback for firing events to dash.
     */
    'fireEvent': PropTypes.func,

    'dashEvents': PropTypes.oneOf(['click']),
    
    'setProps': PropTypes.func
    `
}

function generateComponent(Component, element, attributes) {
    const propTypes = generatePropTypes(element, attributes);

    return `
import React from 'react';
import PropTypes from 'prop-types';

const ${Component} = (props) => {
    return (
        <${element}
            onClick={() => {
                if (props.setProps) {
                    props.setProps({
                        n_clicks: props.n_clicks + 1,
                        n_clicks_timestamp: Date.now()
                    })
                }
                if (props.fireEvent) props.fireEvent({event: 'click'});
            }}
            {...props}
        >
            {props.children}
        </${element}>
    );
};

${Component}.defaultProps = {
    n_clicks: 0,
    n_clicks_timestamp: -1
};

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
