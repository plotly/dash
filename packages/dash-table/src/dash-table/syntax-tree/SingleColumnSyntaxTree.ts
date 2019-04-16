import SyntaxTree from 'core/syntax-tree';
import { ILexemeResult, ILexerResult } from 'core/syntax-tree/lexer';
import { LexemeType, boundLexeme } from 'core/syntax-tree/lexicon';

import { ColumnId } from 'dash-table/components/Table/props';

import operand from './lexeme/operand';
import { equal } from './lexeme/relational';

import columnLexicon from './lexicon/column';

function isBinary(lexemes: ILexemeResult[]) {
    return lexemes.length === 2;
}

function isExpression(lexemes: ILexemeResult[]) {
    return lexemes.length === 1 &&
        lexemes[0].lexeme.type === LexemeType.Expression;
}

function isUnary(lexemes: ILexemeResult[]) {
    return lexemes.length === 1 &&
        lexemes[0].lexeme.type === LexemeType.UnaryOperator;
}

export function modifyLex(key: ColumnId, res: ILexerResult) {
    if (!res.valid) {
        return res;
    }

    if (isBinary(res.lexemes) || isUnary(res.lexemes)) {
        res.lexemes = [
            { lexeme: boundLexeme(operand), value: `{${key}}` },
            ...res.lexemes
        ];
    } else if (isExpression(res.lexemes)) {
        res.lexemes = [
            { lexeme: boundLexeme(operand), value: `{${key}}` },
            { lexeme: boundLexeme(equal), value: 'eq' },
            ...res.lexemes
        ];
    }

    return res;
}

export default class SingleColumnSyntaxTree extends SyntaxTree {
    constructor(key: ColumnId, query: string) {
        super(columnLexicon, query, modifyLex.bind(undefined, key));
    }
}