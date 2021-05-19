module.exports = {
    extends: [
        'eslint:recommended',
        'prettier'
    ],
    plugins: [
        'react',
        'import'
    ],
    env: {
        browser: true
    },
    parser: 'babel-eslint',
    parserOptions: {
        sourceType: 'module',
    },
    rules: {
        'arrow-parens': [2, 'as-needed'],
        'comma-dangle': [2, 'never'],
        'no-unused-expressions': 2,
        'no-unused-vars': 2,
        'prefer-arrow-callback': 2,
        'quote-props': [2, 'as-needed'],
        'quotes': [2, 'single', { 'avoidEscape': true }]
    }
};