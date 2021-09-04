import {ILexeme} from 'core/syntax-tree/lexicon';

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
    isStr
} from '../lexeme/unary';

import {
    ifExpression,
    ifLogicalOperator,
    ifRelationalOperator,
    ifUnaryOperator,
    isTerminalExpression
} from '.';
import {FilterLogicalOperator} from 'dash-table/components/Table/props';

export default function (operator: FilterLogicalOperator): ILexeme[] {
    return [
        {
            ...(operator === FilterLogicalOperator.And ? and : or),
            if: ifLogicalOperator,
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
            terminal: true
        })),
        ...[fieldExpression, stringExpression, valueExpression].map(exp => ({
            ...exp,
            if: ifExpression,
            terminal: isTerminalExpression
        }))
    ];
}
