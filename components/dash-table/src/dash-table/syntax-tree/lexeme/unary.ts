import * as R from 'ramda';

import Logger from 'core/Logger';
import {LexemeType, IUnboundedLexeme} from 'core/syntax-tree/lexicon';
import {ISyntaxTree} from 'core/syntax-tree/syntaxer';

const checkPrimality = (c: number) => {
    if (c === 2) {
        return true;
    }
    if (c < 2 || c % 2 === 0) {
        return false;
    }
    for (let n = 3; n * n <= c; n += 2) {
        if (c % n === 0) {
            return false;
        }
    }
    return true;
};

function evaluator(target: any, tree: ISyntaxTree): any {
    Logger.trace('evaluate -> unary', target, tree);

    Logger.trace('evaluate -> unary', target, tree);

    const t = tree as any;
    const opValue = t.left.lexeme.resolve(target, t.left);

    return opValue;
}

function relationalSyntaxer([left, lexeme]: any[]) {
    return Object.assign({left}, lexeme);
}

function relationalEvaluator(fn: (opValue: any) => boolean) {
    return (target: any, tree: ISyntaxTree) => fn(evaluator(target, tree));
}

enum UnaryOperator {
    Not = '!'
}

const LEXEME_BASE = {
    present: (tree: ISyntaxTree) => tree.value,
    priority: 0,
    syntaxer: relationalSyntaxer,
    type: LexemeType.UnaryOperator
};

export const not: IUnboundedLexeme = {
    evaluate: (target, tree) => {
        Logger.trace('evaluate -> unary not', target, tree);

        const t = tree as any;

        return !t.right.lexeme.evaluate(target, t.right);
    },
    type: LexemeType.UnaryOperator,
    subType: UnaryOperator.Not,
    priority: 1.5,
    regexp: /^!/,
    syntaxer: (lexs: any[]) => {
        return Object.assign(
            {
                right: lexs.slice(1, lexs.length)
            },
            lexs[0]
        );
    }
};

export const isBool: IUnboundedLexeme = R.mergeRight(
    {
        evaluate: relationalEvaluator(opValue => typeof opValue === 'boolean'),
        regexp: /^(is bool)/i
    },
    LEXEME_BASE
);

export const isEven: IUnboundedLexeme = R.mergeRight(
    {
        evaluate: relationalEvaluator(
            opValue => typeof opValue === 'number' && opValue % 2 === 0
        ),
        regexp: /^(is even)/i
    },
    LEXEME_BASE
);

export const isBlank: IUnboundedLexeme = R.mergeRight(
    {
        evaluate: relationalEvaluator(
            opValue =>
                opValue === undefined || opValue === null || opValue === ''
        ),
        regexp: /^(is blank)/i
    },
    LEXEME_BASE
);

export const isNil: IUnboundedLexeme = R.mergeRight(
    {
        evaluate: relationalEvaluator(
            opValue => opValue === undefined || opValue === null
        ),
        regexp: /^(is nil)/i
    },
    LEXEME_BASE
);

export const isNum: IUnboundedLexeme = R.mergeRight(
    {
        evaluate: relationalEvaluator(opValue => typeof opValue === 'number'),
        regexp: /^(is num)/i
    },
    LEXEME_BASE
);

export const isObject: IUnboundedLexeme = R.mergeRight(
    {
        evaluate: relationalEvaluator(
            opValue => opValue !== null && typeof opValue === 'object'
        ),
        regexp: /^(is object)/i
    },
    LEXEME_BASE
);

export const isOdd: IUnboundedLexeme = R.mergeRight(
    {
        evaluate: relationalEvaluator(
            opValue => typeof opValue === 'number' && opValue % 2 === 1
        ),
        regexp: /^(is odd)/i
    },
    LEXEME_BASE
);

export const isPrime: IUnboundedLexeme = R.mergeRight(
    {
        evaluate: relationalEvaluator(
            opValue => typeof opValue === 'number' && checkPrimality(opValue)
        ),
        regexp: /^(is prime)/i
    },
    LEXEME_BASE
);

export const isStr: IUnboundedLexeme = R.mergeRight(
    {
        evaluate: relationalEvaluator(opValue => typeof opValue === 'string'),
        regexp: /^(is str)/i
    },
    LEXEME_BASE
);
