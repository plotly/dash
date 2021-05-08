const config = require('./index');

config.extends = [
    ...config.extends,
    "plugin:@typescript-eslint/eslint-recommended",
    'plugin:@typescript-eslint/recommended'
];

config.plugins = [
    ...config.plugins,
    '@typescript-eslint'
];

delete config.parser;

config.parserOptions = {
    project: './tsconfig.json'
};

config.rules = {
    ...config.rules,
    "no-unused-vars": 0,
    '@typescript-eslint/ban-types': 0,
    '@typescript-eslint/explicit-module-boundary-types': 0,
    '@typescript-eslint/array-type': 0,
    '@typescript-eslint/eofline': 0,
    '@typescript-eslint/max-classes-per-file': 0,
    '@typescript-eslint/max-line-length': 0,
    '@typescript-eslint/member-access': 0,
    '@typescript-eslint/member-ordering': 0,
    '@typescript-eslint/no-conditional-assignment': 0,
    '@typescript-eslint/no-empty': 0,
    '@typescript-eslint/no-empty-function': 0,
    '@typescript-eslint/no-empty-interface': 0,
    '@typescript-eslint/no-explicit-any': 0,
    '@typescript-eslint/no-unused-vars': [2, { 'argsIgnorePattern': '_' }],
    '@typescript-eslint/object-literal-sort-keys': 0,
    '@typescript-eslint/object-literal-shorthand': 0,
    '@typescript-eslint/ordered-imports': 0,
    '@typescript-eslint/prefer-const': 0,
    '@typescript-eslint/prefer-for-of': 0,
    '@typescript-eslint/space-before-function-paren': [0, 'always'],
    '@typescript-eslint/unified-signatures': 0,
    '@typescript-eslint/variable-name': 0
}

module.exports = config;