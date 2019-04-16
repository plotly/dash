import * as R from 'ramda';

import {
    fieldExpression,
    stringExpression,
    valueExpression
} from '../lexeme/expression';
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

import { LexemeType, ILexeme } from 'core/syntax-tree/lexicon';
import { ILexemeResult } from 'core/syntax-tree/lexer';

const lexicon: ILexeme[] = [
    ...[contains,
        equal,
        greaterOrEqual,
        greaterThan,
        lessOrEqual,
        lessThan,
        notEqual
    ].map(op => ({
        ...op,
        terminal: false,
        if: (_lexs: ILexemeResult[], previous: ILexemeResult) => !previous
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
        if: (_lexs: ILexemeResult[], previous: ILexemeResult) => !previous,
        terminal: true
    })),
    ...[
        fieldExpression,
        stringExpression,
        valueExpression
    ].map(exp => ({
        ...exp,
        if: (_lexs: ILexemeResult[], previous: ILexemeResult) =>
            !previous || R.contains(
                previous.lexeme.type,
                [LexemeType.RelationalOperator]
            ),
        terminal: true
    }))
];

export default lexicon;