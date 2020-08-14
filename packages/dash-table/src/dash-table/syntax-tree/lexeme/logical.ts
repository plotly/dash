import Logger from 'core/Logger';
import {LexemeType, IUnboundedLexeme} from 'core/syntax-tree/lexicon';

enum LogicalOperator {
    And = '&&',
    Or = '||'
}

export const and: IUnboundedLexeme = {
    evaluate: (target, tree) => {
        Logger.trace('evaluate -> &&', target, tree);

        const t = tree as any;
        const lv = t.left.lexeme.evaluate(target, t.left);
        const rv = t.right.lexeme.evaluate(target, t.right);
        return lv && rv;
    },
    type: LexemeType.LogicalOperator,
    priority: 2,
    regexp: /^(and\s|&&)/i,
    subType: LogicalOperator.And,
    syntaxer: (lexs: any[], pivot: any, pivotIndex: number) => {
        return Object.assign(
            {
                left: lexs.slice(0, pivotIndex),
                right: lexs.slice(pivotIndex + 1)
            },
            pivot
        );
    }
};

export const or: IUnboundedLexeme = {
    evaluate: (target, tree) => {
        Logger.trace('evaluate -> ||', target, tree);

        const t = tree as any;

        return (
            t.left.lexeme.evaluate(target, t.left) ||
            t.right.lexeme.evaluate(target, t.right)
        );
    },
    type: LexemeType.LogicalOperator,
    subType: LogicalOperator.Or,
    priority: 3,
    regexp: /^(or\s|\|\|)/i,
    syntaxer: (lexs: any[], pivot: any, pivotIndex: number) => {
        return Object.assign(
            {
                left: lexs.slice(0, pivotIndex),
                right: lexs.slice(pivotIndex + 1)
            },
            pivot
        );
    }
};
