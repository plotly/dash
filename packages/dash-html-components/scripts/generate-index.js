'use strict';

/**
 * Generates an export `src/index.js` file from `src/components` directory
 */

const fs = require('fs');
const path = require('path')

const srcPath = '../src';
const componentPath = './components';
const indexFileName = 'index.js';

const components = fs
    .readdirSync(path.join(srcPath, componentPath))
    .filter(component => component.indexOf('.react.js') > -1)
    .map(component => component.replace('.react.js', ''));

let index = components.reduce((indexStr, component) => (
    indexStr + `import ${component} from '${componentPath}/${component}.react';\n`
), '');

index += `\nexport {
${components.map(c => `    ${c}`).join(',\n')}
};\n`;

const indexPath = path.join(srcPath, indexFileName);
console.log(`Writing index for ${components.length} components to ${indexPath}.`);
fs.writeFileSync(indexPath, index);
