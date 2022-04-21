import isNumeric from 'fast-isnumeric';
import * as R from 'ramda';

import Logger from 'core/Logger';
import {LexemeType, IUnboundedLexeme} from 'core/syntax-tree/lexicon';
import {ISyntaxTree} from 'core/syntax-tree/syntaxer';
import {normalizeDate} from 'dash-table/type/date';
import {IDateValidation} from 'dash-table/components/Table/props';

function evaluator(target: any, tree: ISyntaxTree): [any, any, string] {
    Logger.trace('evaluate -> relational', target, tree);

    const t = tree as any;

    const opValue = t.left.lexeme.resolve(target, t.left);
    const expValue = t.right.lexeme.resolve(target, t.right);
    Logger.trace(`opValue: ${opValue}, expValue: ${expValue}`);

    return [opValue, expValue, tree.value];
}

function relationalSyntaxer([left, lexeme, right]: any[]) {
    return Object.assign({left, right}, lexeme);
}

function relationalEvaluator(fn: ([opValue, expValue]: any[]) => boolean) {
    return (target: any, tree: ISyntaxTree) => fn(evaluator(target, tree));
}

export enum RelationalOperator {
    Contains = 'contains',
    DateStartsWith = 'datestartswith',
    Equal = '=',
    GreaterOrEqual = '>=',
    GreaterThan = '>',
    LessOrEqual = '<=',
    LessThan = '<',
    NotEqual = '!='
}

const LEXEME_BASE = {
    priority: 0,
    syntaxer: relationalSyntaxer,
    type: LexemeType.RelationalOperator
};

const containsEval = (lhs: any, rhs: any, relOp: string): boolean =>
    relOp[0] == 'i'
        ? lhs.toString().toUpperCase().indexOf(rhs.toString().toUpperCase()) !==
          -1
        : lhs.toString().indexOf(rhs.toString()) !== -1;

const equalEval = (lhs: any, rhs: any, relOp: string): boolean =>
    isNumeric(lhs) && isNumeric(rhs)
        ? +lhs === +rhs
        : relOp[0] == 'i'
        ? lhs.toString().toUpperCase() === rhs.toString().toUpperCase()
        : lhs === rhs;

const fnEval = (
    fn: (lhs: any, rhs: any) => boolean,
    lhs: any,
    rhs: any,
    relOp: string
): boolean =>
    relOp[0] == 'i'
        ? fn(lhs.toString().toUpperCase(), rhs.toString().toUpperCase())
        : fn(lhs, rhs);

export const contains: IUnboundedLexeme = R.mergeRight(
    {
        evaluate: relationalEvaluator(
            ([lhs, rhs, relOp]) =>
                !R.isNil(rhs) &&
                !R.isNil(lhs) &&
                (R.type(rhs) === 'String' || R.type(lhs) === 'String') &&
                containsEval(lhs, rhs, relOp)
        ),
        subType: RelationalOperator.Contains,
        regexp: /^((i|s)?contains)(?=\s|$)/i,
        regexpFlags: 2,
        regexpMatch: 1
    },
    LEXEME_BASE
);

export const equal: IUnboundedLexeme = R.mergeRight(
    {
        evaluate: relationalEvaluator(([lhs, rhs, relOp]) =>
            equalEval(lhs, rhs, relOp)
        ),
        subType: RelationalOperator.Equal,
        regexp: /^((i|s)?(=|(eq)(?=\s|$)))/i,
        regexpFlags: 2,
        regexpMatch: 1
    },
    LEXEME_BASE
);

export const greaterOrEqual: IUnboundedLexeme = R.mergeRight(
    {
        evaluate: relationalEvaluator(([lhs, rhs, relOp]) =>
            fnEval((l, r) => l >= r, lhs, rhs, relOp)
        ),
        subType: RelationalOperator.GreaterOrEqual,
        regexp: /^((i|s)?(>=|(ge)(?=\s|$)))/i,
        regexpFlags: 2,
        regexpMatch: 1
    },
    LEXEME_BASE
);

export const greaterThan: IUnboundedLexeme = R.mergeRight(
    {
        evaluate: relationalEvaluator(([lhs, rhs, relOp]) =>
            fnEval((l, r) => l > r, lhs, rhs, relOp)
        ),
        subType: RelationalOperator.GreaterThan,
        regexp: /^((i|s)?(>|(gt)(?=\s|$)))/i,
        regexpFlags: 2,
        regexpMatch: 1
    },
    LEXEME_BASE
);

const DATE_OPTIONS: IDateValidation = {
    allow_YY: true
};

export const dateStartsWith: IUnboundedLexeme = R.mergeRight(
    {
        evaluate: relationalEvaluator(([op, exp]) => {
            op = typeof op === 'number' ? op.toString() : op;
            exp = typeof exp === 'number' ? exp.toString() : exp;

            const normalizedOp = normalizeDate(op, DATE_OPTIONS);
            const normalizedExp = normalizeDate(exp, DATE_OPTIONS);

            return (
                !R.isNil(normalizedOp) &&
                !R.isNil(normalizedExp) &&
                // IE11 does not support `startsWith`
                normalizedOp.indexOf(normalizedExp) === 0
            );
        }),
        subType: RelationalOperator.DateStartsWith,
        regexp: /^((datestartswith)(?=\s|$))/i,
        regexpMatch: 1
    },
    LEXEME_BASE
);

export const lessOrEqual: IUnboundedLexeme = R.mergeRight(
    {
        evaluate: relationalEvaluator(([lhs, rhs, relOp]) =>
            fnEval((l, r) => l <= r, lhs, rhs, relOp)
        ),
        subType: RelationalOperator.LessOrEqual,
        regexp: /^((i|s)?(<=|(le)(?=\s|$)))/i,
        regexpFlags: 2,
        regexpMatch: 1
    },
    LEXEME_BASE
);

export const lessThan: IUnboundedLexeme = R.mergeRight(
    {
        evaluate: relationalEvaluator(([lhs, rhs, relOp]) =>
            fnEval((l, r) => l < r, lhs, rhs, relOp)
        ),
        subType: RelationalOperator.LessThan,
        regexp: /^((i|s)?(<|(lt)(?=\s|$)))/i,
        regexpFlags: 2,
        regexpMatch: 1
    },
    LEXEME_BASE
);

export const notEqual: IUnboundedLexeme = R.mergeRight(
    {
        evaluate: relationalEvaluator(([lhs, rhs, relOp]) =>
            fnEval((l, r) => l !== r, lhs, rhs, relOp)
        ),
        subType: RelationalOperator.NotEqual,
        regexp: /^((i|s)?(!=|(ne)(?=\s|$)))/i,
        regexpFlags: 2,
        regexpMatch: 1
    },
    LEXEME_BASE
);
