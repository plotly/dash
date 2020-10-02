#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const reactDocs = require('react-docgen');

function generate (flavor, componentPaths, ignorePattern=new RegExp('^_')) {
    let failed = false;

    const excludedDocProps = [
        'setProps', 'id', 'className', 'style'
    ];

    const reservedPatterns = [
        "UNDEFINED",
        "REQUIRED",
        "to_plotly_json",
        "available_properties",
        "available_wildcard_properties",
        "_.*",
    ].map(i => new RegExp(`^${i}$`));

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

    function propError(doc) {
        for (const propName in doc.props) {
            reservedPatterns.forEach(reservedPattern => {
                if (reservedPattern.test(propName)) {
                    process.stderr.write(
                        `\nERROR: "${propName}" matches reserved word ` +
                        `pattern: ${reservedPattern.toString()}\n`
                    );
                    failed = true;
                }
            });
        }
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
            propError(doc);
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
                if (fs.lstatSync(filepath).isDirectory()
                    && !ignorePattern.test(filename)) {
                    collectMetadataRecursively(filepath);
                } else if (!ignorePattern.test(filename)) {
                    parseFile(filepath);
                }
            });
        } else if (!ignorePattern.test(componentPath)) {
            parseFile(componentPath);
        }
    }

    // execute
    const metadata = Object.create(null);
    componentPaths.forEach(componentPath =>
        collectMetadataRecursively(componentPath)
    );
    if (failed) {
        console.error('\nextract-meta failed.\n');
        process.exit(1);
    }
    else {
        return metadata;
    }
}

module.exports = {
    generate
};