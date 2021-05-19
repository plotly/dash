var path = require('path');

module.exports = {
    "extends": [
        "@plotly/eslint-config-dash/typescript",

    ],
    "parserOptions": {
        "project": path.join(__dirname, "tsconfig.json"),
    },
    "rules": {
        "no-constant-condition": 0,
        "no-prototype-builtins": 0,
        "@typescript-eslint/no-var-requires": 0
    }
};