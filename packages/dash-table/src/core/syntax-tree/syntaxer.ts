import { ILexerResult } from 'core/syntax-tree/lexer';
import { ILexeme } from 'core/syntax-tree/lexicon';
import Logger from 'core/Logger';

export interface ISyntaxTree {
    lexeme: ILexeme;
    block?: ISyntaxTree;
    left?: ISyntaxTree;
    right: ISyntaxTree;
    value: string;
}

export default function parser(lexs: ILexerResult[]): ISyntaxTree {
    let nesting = 0;

    const nestedLexs = lexs.map(lex => {
        const res = Object.assign({}, lex, { nesting: nesting });

        nesting += (lex.lexeme.nesting || 0);

        return res;
    });

    // find lowest priority 0-nesting lex
    const pivot = nestedLexs
        .filter(lex => lex.nesting === 0 && typeof lex.lexeme.priority === 'number')
        .sort((a, b) => (b.lexeme.priority || -1) - (a.lexeme.priority || -1))[0];

    Logger.trace('parser -> pivot', pivot, lexs);

    const pivotIndex = nestedLexs.indexOf(pivot);

    if (pivot.lexeme.syntaxer) {
        let tree = pivot.lexeme.syntaxer(lexs, pivot, pivotIndex);

        if (Array.isArray(tree.left)) {
            tree.left = parser(tree.left);
        }

        if (Array.isArray(tree.right)) {
            tree.right = parser(tree.right);
        }

        if (Array.isArray(tree.block)) {
            tree.block = parser(tree.block);
        }

        return tree;
    } else {
        throw new Error(pivot.lexeme.name);
    }
}