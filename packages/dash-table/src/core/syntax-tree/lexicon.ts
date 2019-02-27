import Logger from 'core/Logger';
import { ISyntaxTree } from 'core/syntax-tree/syntaxer';

export enum LexemeType {
    And = 'and',
    BlockClose = 'close-block',
    BlockOpen = 'open-block',
    BinaryOperator = 'logical-binary-operator',
    Expression = 'expression',
    Or = 'or',
    Operand = 'operand',
    UnaryNot = 'unary-not',
    UnaryOperator = 'logical-unary-operator'
}

export interface ILexeme {
    evaluate?: (target: any, tree: ISyntaxTree) => boolean;
    resolve?: (target: any, tree: ISyntaxTree) => any;
    name: string;
    nesting?: number;
    priority?: number;
    regexp: RegExp;
    syntaxer?: (lexs: any[], pivot: any, pivotIndex: number) => any;
    when?: string[];
}

const isPrime = (c: number) => {
    if (c === 2) { return true; }
    if (c < 2 || c % 2 === 0) { return false; }
    for (let n = 3; n * n <= c; n += 2) { if (c % n === 0) { return false; } }
    return true;
};

const operand = {
    resolve: (target: any, tree: ISyntaxTree) => {
        if (/^(('([^'\\]|\\.)+')|("([^"\\]|\\.")+")|(`([^`\\]|\\.)+`))$/.test(tree.value)) {
            return target[
                tree.value.slice(1, tree.value.length - 1)
            ];
        } else if (/^(\w|[:.\-+])+$/.test(tree.value)) {
            return target[tree.value];
        }
    },
    regexp: /^(('([^'\\]|\\.)+')|("([^"\\]|\\.)+")|(`([^`\\]|\\.)+`)|(\w|[:.\-+])+)/
};

const expression = {
    resolve: (target: any, tree: ISyntaxTree) => {
        if (/^(('([^'\\]|\\.)+')|("([^"\\]|\\.)+")|(`([^`\\]|\\.)+`))$/.test(tree.value)) {
            return tree.value.slice(1, tree.value.length - 1);
        } else if (/^(num|str)\(.*\)$/.test(tree.value)) {
            const res = tree.value.match(/^(\w+)\((.*)\)$/);
            if (res) {
                const [, op, value] = res;

                switch (op) {
                    case 'num':
                        return parseFloat(value);
                    case 'str':
                    default:
                        return value;
                }
            } else {
                throw Error();
            }
        } else {
            return target[tree.value];
        }
    },
    regexp: /^(((num|str)\([^()]*\))|('([^'\\]|\\.)+')|("([^"\\]|\\.)+")|(`([^`\\]|\\.)+`)|(\w|[:.\-+])+)/
};

const lexicon: ILexeme[] = [
    {
        evaluate: (target, tree) => {
            Logger.trace('evalute -> &&', target, tree);

            const t = tree as any;
            const lv = t.left.lexeme.evaluate(target, t.left);
            const rv = t.right.lexeme.evaluate(target, t.right);
            return lv && rv;
        },
        name: LexemeType.And,
        priority: 2,
        regexp: /^(and\s|&&)/i,
        syntaxer: (lexs: any[], pivot: any, pivotIndex: number) => {
            return Object.assign({
                left: lexs.slice(0, pivotIndex),
                right: lexs.slice(pivotIndex + 1)
            }, pivot);
        }
    },
    {
        evaluate: (target, tree) => {
            Logger.trace('evalute -> ||', target, tree);

            const t = tree as any;

            return t.left.lexeme.evaluate(target, t.left) ||
                t.right.lexeme.evaluate(target, t.right);
        },
        name: LexemeType.Or,
        priority: 3,
        regexp: /^(or\s|\|\|)/i,
        syntaxer: (lexs: any[], pivot: any, pivotIndex: number) => {
            return Object.assign({
                left: lexs.slice(0, pivotIndex),
                right: lexs.slice(pivotIndex + 1)
            }, pivot);
        }
    },
    {
        name: LexemeType.BlockClose,
        nesting: -1,
        regexp: /^\)/
    },
    {
        evaluate: (target, tree) => {
            Logger.trace('evaluate -> ()', target, tree);

            const t = tree as any;

            return t.block.lexeme.evaluate(target, t.block);
        },
        name: LexemeType.BlockOpen,
        nesting: 1,
        priority: 1,
        regexp: /^\(/,
        syntaxer: (lexs: any[]) => {
            return Object.assign({
                block: lexs.slice(1, lexs.length - 1)
            }, lexs[0]);
        },
        when: [LexemeType.UnaryNot]
    },
    {
        ...operand,
        name: LexemeType.Operand
    },
    {
        evaluate: (target, tree) => {
            Logger.trace('evaluate -> binary', target, tree);

            const t = tree as any;

            const opValue = t.left.lexeme.resolve(target, t.left);
            const expValue = t.right.lexeme.resolve(target, t.right);
            Logger.trace(`opValue: ${opValue}, expValue: ${expValue}`);

            switch (tree.value.toLowerCase()) {
                case 'eq':
                case '=':
                    return opValue === expValue;
                case 'gt':
                case '>':
                    return opValue > expValue;
                case 'ge':
                case '>=':
                    return opValue >= expValue;
                case 'lt':
                case '<':
                    return opValue < expValue;
                case 'le':
                case '<=':
                    return opValue <= expValue;
                case 'ne':
                case '!=':
                    return opValue !== expValue;
                default:
                    throw new Error();
            }
        },
        name: LexemeType.BinaryOperator,
        priority: 0,
        regexp: /^(>=|<=|>|<|!=|=|ge|le|gt|lt|eq|ne)/i,
        syntaxer: (lexs: any[]) => {
            let [left, lexeme, right] = lexs;

            return Object.assign({ left, right }, lexeme);
        },
        when: [LexemeType.Operand]
    },
    {
        evaluate: (target, tree) => {
            Logger.trace('evaluate -> unary', target, tree);

            const t = tree as any;
            const opValue = t.block.lexeme.resolve(target, t.block);

            switch (tree.value.toLowerCase()) {
                case 'is even':
                    return typeof opValue === 'number' && opValue % 2 === 0;
                case 'is nil':
                    return opValue === undefined || opValue === null;
                case 'is bool':
                    return typeof opValue === 'boolean';
                case 'is odd':
                    return typeof opValue === 'number' && opValue % 2 === 1;
                case 'is num':
                    return typeof opValue === 'number';
                case 'is object':
                    return opValue !== null && typeof opValue === 'object';
                case 'is str':
                    return typeof opValue === 'string';
                case 'is prime':
                    return typeof opValue === 'number' && isPrime(opValue);
                default:
                    throw new Error();
            }
        },
        name: LexemeType.UnaryOperator,
        priority: 0,
        regexp: /^((is nil)|(is odd)|(is even)|(is bool)|(is num)|(is object)|(is str)|(is prime))/i,
        syntaxer: (lexs: any[]) => {
            let [block, lexeme] = lexs;

            return Object.assign({ block }, lexeme);
        },
        when: [LexemeType.Operand]
    },
    {
        evaluate: (target, tree) => {
            Logger.trace('evaluate -> unary not', target, tree);

            const t = tree as any;

            return !t.block.lexeme.evaluate(target, t.block);
        },
        name: LexemeType.UnaryNot,
        priority: 1.5,
        regexp: /^!/,
        syntaxer: (lexs: any[]) => {
            return Object.assign({
                block: lexs.slice(1, lexs.length)
            }, lexs[0]);
        },
        when: [LexemeType.UnaryNot]
    },
    {
        ...expression,
        name: LexemeType.Expression,
        when: [LexemeType.BinaryOperator]
    }
];

export default lexicon;