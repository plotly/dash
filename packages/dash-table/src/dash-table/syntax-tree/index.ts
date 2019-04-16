import * as R from 'ramda';

import { LexemeType } from 'core/syntax-tree/lexicon';

import MultiColumnsSyntaxTree from './MultiColumnsSyntaxTree';
import QuerySyntaxTree from './QuerySyntaxTree';
import SingleColumnSyntaxTree from './SingleColumnSyntaxTree';
import { RelationalOperator } from './lexeme/relational';

export const getMultiColumnQueryString = (
    asts: SingleColumnSyntaxTree[]
) => R.map(
    ast => ast.toQueryString(),
    R.filter(ast => ast && ast.isValid, asts)
    ).join(' && ');

export const getSingleColumnMap = (ast: MultiColumnsSyntaxTree) => {
    if (!ast.isValid) {
        return;
    }

    const map = new Map<string, SingleColumnSyntaxTree>();

    const statements = ast.statements;
    if (!statements) {
        return map;
    }

    R.forEach(s => {
        if (s.lexeme.type === LexemeType.UnaryOperator && s.left) {
            const sanitizedColumnId = s.left.lexeme.present ? s.left.lexeme.present(s.left) : s.left.value;
            map.set(sanitizedColumnId, new SingleColumnSyntaxTree(sanitizedColumnId, s.value));
        } else if (s.lexeme.type === LexemeType.RelationalOperator && s.left && s.right) {
            const sanitizedColumnId = s.left.lexeme.present ? s.left.lexeme.present(s.left) : s.left.value;

            if (s.lexeme.present && s.lexeme.present(s) === RelationalOperator.Equal) {
                map.set(sanitizedColumnId, new SingleColumnSyntaxTree(sanitizedColumnId, `${s.right.value}`));
            } else {
                map.set(sanitizedColumnId, new SingleColumnSyntaxTree(sanitizedColumnId, `${s.value} ${s.right.value}`));
            }
        }
    }, statements);

    return map;
};

export { MultiColumnsSyntaxTree, QuerySyntaxTree, SingleColumnSyntaxTree };