import Logger from 'core/Logger';
import {ILexemeResult, ILexerResult} from 'core/syntax-tree/lexer';
import {ILexeme} from 'core/syntax-tree/lexicon';

export interface ISyntaxerResult {
    tree?: ISyntaxTree;
    valid: boolean;
    error?: string;
}

export interface ISyntaxTree {
    lexeme: ILexeme;
    block?: ISyntaxTree;
    left?: ISyntaxTree;
    right: ISyntaxTree;
    value: string;
}

const parser = (lexs: ILexemeResult[]): ISyntaxTree => {
    let nesting = 0;

    const nestedLexs = lexs.map(lex => {
        const res = Object.assign({}, lex, {nesting});

        nesting += lex.lexeme.nesting || 0;

        return res;
    });

    // find lowest priority 0-nesting lex
    const pivot = nestedLexs
        .filter(
            lex => lex.nesting === 0 && typeof lex.lexeme.priority === 'number'
        )
        .sort(
            (a, b) => (b.lexeme.priority || -1) - (a.lexeme.priority || -1)
        )[0];

    Logger.trace('parser -> pivot', pivot, lexs);

    const pivotIndex = nestedLexs.indexOf(pivot);

    if (pivot.lexeme.syntaxer) {
        const tree = pivot.lexeme.syntaxer(lexs, pivot, pivotIndex);

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
        throw new Error(pivot.lexeme.type);
    }
};

export default (lexerResult: ILexerResult): ISyntaxerResult => {
    const {lexemes} = lexerResult;

    if (!lexerResult.valid) {
        return {valid: false, error: `lexer -- ${lexerResult.error}`};
    }

    if (lexerResult.lexemes.length === 0) {
        return {valid: true};
    }

    try {
        return {tree: parser(lexemes), valid: true};
    } catch (error) {
        return {valid: false, error: String(error)};
    }
};
