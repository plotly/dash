import * as R from 'ramda';

import {ILexemeResult} from 'core/syntax-tree/lexer';
import {LexemeType, ILexeme} from 'core/syntax-tree/lexicon';

import {blockClose, blockOpen} from '../lexeme/block';
import {
    fieldExpression,
    stringExpression,
    valueExpression
} from '../lexeme/expression';
import {and, or} from '../lexeme/logical';
import {
    contains,
    dateStartsWith,
    equal,
    greaterOrEqual,
    greaterThan,
    lessOrEqual,
    lessThan,
    notEqual
} from '../lexeme/relational';
import {
    isBlank,
    isBool,
    isEven,
    isNil,
    isNum,
    isObject,
    isOdd,
    isPrime,
    isStr,
    not
} from '../lexeme/unary';

import {
    ifBlockClose,
    ifBlockOpen,
    ifExpression,
    ifLogicalOperator,
    ifRelationalOperator,
    ifUnaryOperator,
    isTerminal,
    isTerminalExpression
} from '.';

const ifNotUnaryOperator = (
    _: ILexemeResult[],
    previous: ILexemeResult | undefined
) =>
    !previous ||
    R.includes(previous.lexeme.type, [
        LexemeType.LogicalOperator,
        LexemeType.UnaryOperator
    ]);

const lexicon: ILexeme[] = [
    ...[and, or].map(op => ({
        ...op,
        if: ifLogicalOperator,
        terminal: false
    })),
    {
        ...blockClose,
        if: ifBlockClose,
        terminal: isTerminal
    },
    {
        ...blockOpen,
        if: ifBlockOpen,
        terminal: false
    },
    ...[
        contains,
        dateStartsWith,
        equal,
        greaterOrEqual,
        greaterThan,
        lessOrEqual,
        lessThan,
        notEqual
    ].map(op => ({
        ...op,
        if: ifRelationalOperator,
        terminal: false
    })),
    ...[
        isBlank,
        isBool,
        isEven,
        isNil,
        isNum,
        isObject,
        isOdd,
        isPrime,
        isStr
    ].map(op => ({
        ...op,
        if: ifUnaryOperator,
        terminal: isTerminal
    })),
    {
        ...not,
        if: ifNotUnaryOperator,
        terminal: false
    },
    ...[fieldExpression, stringExpression, valueExpression].map(exp => ({
        ...exp,
        if: ifExpression,
        terminal: isTerminalExpression
    }))
];

export default lexicon;
