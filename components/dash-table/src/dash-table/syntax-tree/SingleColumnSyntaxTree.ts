import * as R from 'ramda';

import {RequiredPluck, OptionalPluck} from 'core/type';
import SyntaxTree from 'core/syntax-tree';
import {ILexemeResult, ILexerResult} from 'core/syntax-tree/lexer';
import {LexemeType, boundLexeme} from 'core/syntax-tree/lexicon';

import {
    ColumnType,
    FilterCase,
    IColumn,
    IFilterOptions
} from 'dash-table/components/Table/props';

import {fieldExpression} from './lexeme/expression';
import {
    equal,
    RelationalOperator,
    contains,
    dateStartsWith
} from './lexeme/relational';

import columnLexicon from './lexicon/column';

const sensitiveRelationalOperators: string[] = [
    RelationalOperator.Contains,
    RelationalOperator.Equal,
    RelationalOperator.GreaterOrEqual,
    RelationalOperator.GreaterThan,
    RelationalOperator.LessOrEqual,
    RelationalOperator.LessThan,
    RelationalOperator.NotEqual
];

function getFilterLexeme(
    filterOptions: IFilterOptions | undefined,
    lexeme: ILexemeResult
): ILexemeResult {
    const flags = R.isNil(filterOptions)
        ? ''
        : filterOptions.case === FilterCase.Insensitive
        ? 'i'
        : 's';

    if (
        lexeme.lexeme.type === LexemeType.RelationalOperator &&
        lexeme.lexeme.subType &&
        sensitiveRelationalOperators.indexOf(lexeme.lexeme.subType) !== -1 &&
        lexeme.value &&
        ['i', 's'].indexOf(lexeme.value[0]) === -1
    ) {
        return {
            ...lexeme,
            value: `${flags}${lexeme.value}`
        };
    }

    return lexeme;
}

function getImplicitLexeme(
    filterOptions: IFilterOptions | undefined,
    type: ColumnType = ColumnType.Any
): ILexemeResult {
    const flags = R.isNil(filterOptions)
        ? ''
        : filterOptions.case === FilterCase.Insensitive
        ? 'i'
        : 's';

    switch (type) {
        case ColumnType.Any:
        case ColumnType.Text:
            return {
                lexeme: boundLexeme(contains),
                value: `${flags}${RelationalOperator.Contains}`
            };
        case ColumnType.Datetime:
            return {
                lexeme: boundLexeme(dateStartsWith),
                value: RelationalOperator.DateStartsWith
            };
        case ColumnType.Numeric:
            return {
                lexeme: boundLexeme(equal),
                value: `${flags}${RelationalOperator.Equal}`
            };
    }
}

function isBinary(lexemes: ILexemeResult[]) {
    return lexemes.length === 2;
}

function isExpression(lexemes: ILexemeResult[]) {
    return (
        lexemes.length === 1 && lexemes[0].lexeme.type === LexemeType.Expression
    );
}

function isUnary(lexemes: ILexemeResult[]) {
    return (
        lexemes.length === 1 &&
        lexemes[0].lexeme.type === LexemeType.UnaryOperator
    );
}

function modifyLex(config: SingleColumnConfig, res: ILexerResult) {
    if (!res.valid) {
        return res;
    }

    if (isBinary(res.lexemes)) {
        res.lexemes = [
            {lexeme: boundLexeme(fieldExpression), value: `{${config.id}}`},
            getFilterLexeme(config.filter_options, res.lexemes[0]),
            res.lexemes[1]
        ];
    } else if (isUnary(res.lexemes)) {
        res.lexemes = [
            {lexeme: boundLexeme(fieldExpression), value: `{${config.id}}`},
            ...res.lexemes
        ];
    } else if (isExpression(res.lexemes)) {
        res.lexemes = [
            {lexeme: boundLexeme(fieldExpression), value: `{${config.id}}`},
            getImplicitLexeme(config.filter_options, config.type),
            ...res.lexemes
        ];
    }

    return res;
}

export type SingleColumnConfig = RequiredPluck<IColumn, 'id'> &
    OptionalPluck<IColumn, 'filter_options'> &
    OptionalPluck<IColumn, 'type'>;

export default class SingleColumnSyntaxTree extends SyntaxTree {
    constructor(query: string, config: SingleColumnConfig) {
        super(columnLexicon, query, modifyLex.bind(undefined, config));
    }
}
