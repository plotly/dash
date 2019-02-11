#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const reactDocs = require('react-docgen');

const componentPaths = process.argv.slice(3);
const ignorePattern = new RegExp(process.argv[2]);

const excludedDocProps = [
    'setProps', 'id', 'className', 'style'
];

if (!componentPaths.length) {
    help();
    process.exit(1);
}

const metadata = Object.create(null);
componentPaths.forEach(componentPath =>
    collectMetadataRecursively(componentPath)
);
writeOut(metadata);

function help() {
    console.error('usage: ');
    console.error(
        'extract-meta path/to/component(s) ' +
            ' [path/to/more/component(s), ...] > metadata.json'
    );
}

function writeError(msg, filePath) {
    if (filePath) {
        process.stderr.write(`Error with path ${filePath}`);
    }

    process.stderr.write(msg + '\n');
    if (msg instanceof Error) {
        process.stderr.write(msg.stack + '\n');
    }
}

function checkWarn(name, value) {
    if (!value || (value.length < 1 && !excludedDocProps.includes(name.split('.').pop()))) {
        process.stderr.write(`\nDescription for ${name} is missing!\n`)
    }
}

function docstringWarning(doc) {
    checkWarn(doc.displayName, doc.description);

    Object.entries(doc.props).forEach(
        ([name, p]) => checkWarn(`${doc.displayName}.${name}`, p.description)
    );
}


function parseFile(filepath) {
    const urlpath = filepath.split(path.sep).join('/');
    let src;

    if (!['.jsx', '.js'].includes(path.extname(filepath))) {
        return;
    }

    try {
        src = fs.readFileSync(filepath);
        const doc = metadata[urlpath] = reactDocs.parse(src);
        docstringWarning(doc);
    } catch (error) {
        writeError(error, filepath);
    }
}

function collectMetadataRecursively(componentPath) {
    if (ignorePattern.test(componentPath)) {
        return;
    }
    if (fs.lstatSync(componentPath).isDirectory()) {
        let dirs;
        try {
            dirs = fs.readdirSync(componentPath);
        } catch (error) {
            writeError(error, componentPath);
        }
        dirs.forEach(filename => {
            const filepath = path.join(componentPath, filename);
            if (fs.lstatSync(filepath).isDirectory()) {
                collectMetadataRecursively(filepath);
            } else if (!ignorePattern.test(filename)) {
                parseFile(filepath);
            }
        });
    } else if (!ignorePattern.test(componentPath)) {
        parseFile(componentPath);
    }
}

function writeOut(result) {
    console.log(JSON.stringify(result, '\t', 2));
}
