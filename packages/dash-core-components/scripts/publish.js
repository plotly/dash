#! /usr/bin/env node

const execSh = require('exec-sh');
let version = require('../package.json').version;
let name = require('../package.json').name.replace(/-/g, '_');

if(version.includes("rc")) {
    version = version.replace('-', '');
    console.log("Adjusted version to", version, "for PyPi");
}

console.log(`Publishing version ${version} of ${name} to NPM & PyPi\n`);

console.log('>', 'python setup.py sdist');

execSh('git diff-index --quiet HEAD --', err => {
    if(err) {
        throw new Error('\nIt looks like there are uncommitted changes! Aborting until these changes have been resolved.\n');
    } else {
        execSh([
                'npm publish --otp',
                `python setup.py sdist`,
                `twine upload dist/${name}-${version}.tar.gz`,
                `git tag -a 'v${version}' -m 'v${version}'`,
                `git push origin v${version}`
            ]
            , err => {
                if(err) {
                    throw new Error(err);
                }
        });
    }
})
