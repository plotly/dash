import isNumeric from 'fast-isnumeric';

import {LexemeType, IUnboundedLexeme} from 'core/syntax-tree/lexicon';
import {ISyntaxTree} from 'core/syntax-tree/syntaxer';

const FIELD_REGEX = /^{(([^{}\\]|\\.)+)}/;
const STRING_REGEX = /^(('([^'\\]|\\.)*')|("([^"\\]|\\.)*")|(`([^`\\]|\\.)*`))/;
const VALUE_REGEX = /^(([^\s'"`{}()\\]|\\.)+)(?:[\s)]|$)/;
const PERMISSIVE_VALUE_REGEX = /^(([^'"`{}()\\]|\\.)+)$/;

const getField = (value: string) =>
    value.slice(1, value.length - 1).replace(/\\(.)/g, '$1');

export const fieldExpression: IUnboundedLexeme = {
    present: (tree: ISyntaxTree) => getField(tree.value),
    resolve: (target: any, tree: ISyntaxTree) => {
        if (FIELD_REGEX.test(tree.value)) {
            return target[getField(tree.value)];
        } else {
            throw new Error();
        }
    },
    regexp: FIELD_REGEX,
    subType: 'field',
    type: LexemeType.Expression
};

const getString = (value: string) =>
    value.slice(1, value.length - 1).replace(/\\(.)/g, '$1');

export const stringExpression: IUnboundedLexeme = {
    present: (tree: ISyntaxTree) => getString(tree.value),
    resolve: (_target: any, tree: ISyntaxTree) => {
        if (STRING_REGEX.test(tree.value)) {
            return getString(tree.value);
        } else {
            throw new Error();
        }
    },
    regexp: STRING_REGEX,
    subType: 'value',
    type: LexemeType.Expression
};

const getValueFactory = (regex: RegExp) => (value: string) => {
    value = (value.match(regex) as any)[1];

    return isNumeric(value) ? +value : value.replace(/\\(.)/g, '$1');
};

const valueExpressionFactory = (
    regex: RegExp,
    transform?: (v: any) => any
): IUnboundedLexeme => {
    const getValue = getValueFactory(regex);

    return {
        present: (tree: ISyntaxTree) => getValue(tree.value),
        resolve: (_target: any, tree: ISyntaxTree) => {
            if (regex.test(tree.value)) {
                return getValue(tree.value);
            } else {
                throw new Error();
            }
        },
        regexp: regex,
        regexpMatch: 1,
        subType: 'value',
        transform,
        type: LexemeType.Expression
    };
};

export const valueExpression = valueExpressionFactory(VALUE_REGEX);
export const permissiveValueExpression = valueExpressionFactory(
    PERMISSIVE_VALUE_REGEX,
    (v: any) => (typeof v === 'string' && v.indexOf(' ') !== -1 ? `"${v}"` : v)
);
