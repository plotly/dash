import isNumeric from 'fast-isnumeric';
import * as R from 'ramda';

import Logger from 'core/Logger';
import {LexemeType, IUnboundedLexeme} from 'core/syntax-tree/lexicon';
import {ISyntaxTree} from 'core/syntax-tree/syntaxer';
import {normalizeDate} from 'dash-table/type/date';
import {IDateValidation} from 'dash-table/components/Table/props';

function evaluator(target: any, tree: ISyntaxTree): [any, any] {
    Logger.trace('evaluate -> relational', target, tree);

    const t = tree as any;

    const opValue = t.left.lexeme.resolve(target, t.left);
    const expValue = t.right.lexeme.resolve(target, t.right);
    Logger.trace(`opValue: ${opValue}, expValue: ${expValue}`);

    return [opValue, expValue];
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

export const contains: IUnboundedLexeme = R.merge(
    {
        evaluate: relationalEvaluator(
            ([op, exp]) =>
                !R.isNil(exp) &&
                !R.isNil(op) &&
                (R.type(exp) === 'String' || R.type(op) === 'String') &&
                op.toString().indexOf(exp.toString()) !== -1
        ),
        subType: RelationalOperator.Contains,
        regexp: /^((contains)(?=\s|$))/i,
        regexpMatch: 1
    },
    LEXEME_BASE
);

export const equal: IUnboundedLexeme = R.merge(
    {
        evaluate: relationalEvaluator(([op, exp]) =>
            isNumeric(op) && isNumeric(exp) ? +op === +exp : op === exp
        ),
        subType: RelationalOperator.Equal,
        regexp: /^(=|(eq)(?=\s|$))/i,
        regexpMatch: 1
    },
    LEXEME_BASE
);

export const greaterOrEqual: IUnboundedLexeme = R.merge(
    {
        evaluate: relationalEvaluator(([op, exp]) => op >= exp),
        subType: RelationalOperator.GreaterOrEqual,
        regexp: /^(>=|(ge)(?=\s|$))/i,
        regexpMatch: 1
    },
    LEXEME_BASE
);

export const greaterThan: IUnboundedLexeme = R.merge(
    {
        evaluate: relationalEvaluator(([op, exp]) => op > exp),
        subType: RelationalOperator.GreaterThan,
        regexp: /^(>|(gt)(?=\s|$))/i,
        regexpMatch: 1
    },
    LEXEME_BASE
);

const DATE_OPTIONS: IDateValidation = {
    allow_YY: true
};

export const dateStartsWith: IUnboundedLexeme = R.merge(
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

export const lessOrEqual: IUnboundedLexeme = R.merge(
    {
        evaluate: relationalEvaluator(([op, exp]) => op <= exp),
        subType: RelationalOperator.LessOrEqual,
        regexp: /^(<=|(le)(?=\s|$))/i,
        regexpMatch: 1
    },
    LEXEME_BASE
);

export const lessThan: IUnboundedLexeme = R.merge(
    {
        evaluate: relationalEvaluator(([op, exp]) => op < exp),
        subType: RelationalOperator.LessThan,
        regexp: /^(<|(lt)(?=\s|$))/i,
        regexpMatch: 1
    },
    LEXEME_BASE
);

export const notEqual: IUnboundedLexeme = R.merge(
    {
        evaluate: relationalEvaluator(([op, exp]) => op !== exp),
        subType: RelationalOperator.NotEqual,
        regexp: /^(!=|(ne)(?=\s|$))/i,
        regexpMatch: 1
    },
    LEXEME_BASE
);
