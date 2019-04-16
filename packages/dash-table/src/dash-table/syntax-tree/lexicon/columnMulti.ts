import * as R from 'ramda';

import {
    fieldExpression,
    stringExpression,
    valueExpression
} from '../lexeme/expression';
import {
    and
} from '../lexeme/logical';
import operand from '../lexeme/operand';
import {
    contains,
    equal,
    greaterOrEqual,
    greaterThan,
    lessOrEqual,
    lessThan,
    notEqual
} from '../lexeme/relational';
import {
    isBool,
    isEven,
    isNil,
    isNum,
    isObject,
    isOdd,
    isPrime,
    isStr
} from '../lexeme/unary';

import { ILexeme, LexemeType } from 'core/syntax-tree/lexicon';
import { ILexemeResult } from 'core/syntax-tree/lexer';

const lexicon: ILexeme[] = [
    {
        ...and,
        if: (_: ILexemeResult[], previous: ILexemeResult) =>
            previous && R.contains(
                previous.lexeme.type,
                [
                    LexemeType.Expression,
                    LexemeType.UnaryOperator
                ]
            ),
        terminal: false
    },
    {
        ...operand,
        if: (_: ILexemeResult[], previous: ILexemeResult) =>
            !previous || R.contains(
                previous.lexeme.type,
                [LexemeType.LogicalOperator]
            ),
        terminal: false
    },
    ...[contains,
        equal,
        greaterOrEqual,
        greaterThan,
        lessOrEqual,
        lessThan,
        notEqual
    ].map(op => ({
        ...op,
        if: (_: ILexemeResult[], previous: ILexemeResult) =>
            previous && R.contains(
                previous.lexeme.type,
                [LexemeType.Operand]
            ),
        terminal: false
    })),
    ...[isBool,
        isEven,
        isNil,
        isNum,
        isObject,
        isOdd,
        isPrime,
        isStr
    ].map(op => ({
        ...op,
        if: (_: ILexemeResult[], previous: ILexemeResult) =>
            previous && R.contains(
                previous.lexeme.type,
                [LexemeType.Operand]
            ),
        terminal: true
    })),
    ...[
        fieldExpression,
        stringExpression,
        valueExpression
    ].map(exp => ({
        ...exp,
        if: (_: ILexemeResult[], previous: ILexemeResult) =>
            previous && R.contains(
                previous.lexeme.type,
                [LexemeType.RelationalOperator]
            ),
        terminal: true
    }))
];

export default lexicon;