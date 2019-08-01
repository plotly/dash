import { RequiredPluck, OptionalPluck } from 'core/type';
import SyntaxTree from 'core/syntax-tree';
import { ILexemeResult, ILexerResult } from 'core/syntax-tree/lexer';
import { LexemeType, boundLexeme } from 'core/syntax-tree/lexicon';

import { ColumnType, IColumn } from 'dash-table/components/Table/props';

import { fieldExpression } from './lexeme/expression';
import { equal, RelationalOperator } from './lexeme/relational';

import columnLexicon from './lexicon/column';

function getDefaultRelationalOperator(type: ColumnType = ColumnType.Any): RelationalOperator {
    switch (type) {
        case ColumnType.Any:
        case ColumnType.Text:
            return RelationalOperator.Contains;
        case ColumnType.Datetime:
            return RelationalOperator.DateStartsWith;
        case ColumnType.Numeric:
            return RelationalOperator.Equal;
    }
}

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

function modifyLex(config: SingleColumnConfig, res: ILexerResult) {
    if (!res.valid) {
        return res;
    }

    if (isBinary(res.lexemes) || isUnary(res.lexemes)) {
        res.lexemes = [
            { lexeme: boundLexeme(fieldExpression), value: `{${config.id}}` },
            ...res.lexemes
        ];
    } else if (isExpression(res.lexemes)) {
        res.lexemes = [
            { lexeme: boundLexeme(fieldExpression), value: `{${config.id}}` },
            {
                lexeme: boundLexeme(equal),
                value: getDefaultRelationalOperator(config.type)
            },
            ...res.lexemes
        ];
    }

    return res;
}

export type SingleColumnConfig = RequiredPluck<IColumn, 'id'> & OptionalPluck<IColumn, 'type'>;

export default class SingleColumnSyntaxTree extends SyntaxTree {
    constructor(query: string, config: SingleColumnConfig) {
        super(
            columnLexicon,
            query,
            modifyLex.bind(undefined, config)
        );
    }
}