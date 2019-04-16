import isNumeric from 'fast-isnumeric';
import * as R from 'ramda';

import { LexemeType, IUnboundedLexeme } from 'core/syntax-tree/lexicon';
import { ISyntaxTree } from 'core/syntax-tree/syntaxer';
import operand from './operand';

const STRING_REGEX = /^(('([^'\\]|\\.)+')|("([^"\\]|\\.)+")|(`([^`\\]|\\.)+`))/;
const VALUE_REGEX = /^(([^\s'"`{}()\\]|\\.)+)(?:[\s)]|$)/;

export const fieldExpression: IUnboundedLexeme = R.merge(
    operand, {
        subType: 'field',
        type: LexemeType.Expression
    }
);

const getString = (
    value: string
) => value.slice(1, value.length - 1).replace(/\\(.)/g, '$1');

const getValue = (
    value: string
) => {
    value = (value.match(VALUE_REGEX) as any)[1];

    return isNumeric(value) ?
        +value :
        value.replace(/\\(.)/g, '$1');
};

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

export const valueExpression: IUnboundedLexeme = {
    present: (tree: ISyntaxTree) => getValue(tree.value),
    resolve: (_target: any, tree: ISyntaxTree) => {
        if (VALUE_REGEX.test(tree.value)) {
            return getValue(tree.value);
        } else {
            throw new Error();
        }
    },
    regexp: VALUE_REGEX,
    regexpMatch: 1,
    subType: 'value',
    type: LexemeType.Expression
};