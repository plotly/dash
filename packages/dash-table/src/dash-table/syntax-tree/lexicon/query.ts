import * as R from 'ramda';

import {
    blockClose,
    blockOpen
} from '../lexeme/block';
import {
    fieldExpression,
    stringExpression,
    valueExpression
} from '../lexeme/expression';
import {
    and,
    or
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
    isStr,
    not
} from '../lexeme/unary';

import { ILexemeResult } from 'core/syntax-tree/lexer';
import { LexemeType, ILexeme } from 'core/syntax-tree/lexicon';

const nestingReducer = R.reduce<ILexemeResult, number>(
    (nesting, l) => nesting + (l.lexeme.nesting || 0)
);

const isTerminal = (lexemes: ILexemeResult[], previous: ILexemeResult) =>
    previous && nestingReducer(0, lexemes) === 0;

const ifExpression = (_: ILexemeResult[], previous: ILexemeResult) =>
    previous && R.contains(
        previous.lexeme.type,
        [LexemeType.RelationalOperator]
    );

const ifLogicalOperator = (_: ILexemeResult[], previous: ILexemeResult) =>
    previous && R.contains(
        previous.lexeme.type,
        [
            LexemeType.BlockClose,
            LexemeType.Expression,
            LexemeType.UnaryOperator
        ]
    );

const ifOperator = (_: ILexemeResult[], previous: ILexemeResult) =>
    previous && R.contains(
        previous.lexeme.type,
        [LexemeType.Operand]
    );

const lexicon: ILexeme[] = [
    {
        ...and,
        if: ifLogicalOperator,
        terminal: false
    },
    {
        ...or,
        if: ifLogicalOperator,
        terminal: false
    },
    {
        ...blockClose,
        if: (lexemes: ILexemeResult[], previous: ILexemeResult) =>
            previous && R.contains(
                previous.lexeme.type,
                [
                    LexemeType.BlockClose,
                    LexemeType.BlockOpen,
                    LexemeType.Expression,
                    LexemeType.UnaryOperator
                ]
            ) && nestingReducer(0, lexemes) > 0,
        terminal: isTerminal
    },
    {
        ...blockOpen,
        if: (_: ILexemeResult[], previous: ILexemeResult) =>
            !previous || R.contains(
                previous.lexeme.type,
                [
                    LexemeType.BlockOpen,
                    LexemeType.LogicalOperator,
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
                [
                    LexemeType.BlockOpen,
                    LexemeType.LogicalOperator
                ]
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
        if: ifOperator,
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
        if: ifOperator,
        terminal: isTerminal
    })),
    {
        ...not,
        if: (_: ILexemeResult[], previous: ILexemeResult) =>
            !previous || R.contains(
                previous.lexeme.type,
                [
                    LexemeType.LogicalOperator,
                    LexemeType.UnaryOperator
                ]
            ),
        terminal: false
    },
    ...[
        fieldExpression,
        stringExpression,
        valueExpression
    ].map(exp => ({
        ...exp,
        if: ifExpression,
        terminal: isTerminal
    }))
];

export default lexicon;