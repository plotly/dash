import Lexicon, { ILexeme } from 'core/syntax-tree/lexicon';

export interface ILexerResult {
    lexemes: ILexemeResult[];
    valid: boolean;
    error?: string;
}

export interface ILexemeResult {
    lexeme: ILexeme;
    value?: string;
}

export default function lexer(query: string): ILexerResult {
    let lexeme: ILexeme | null = null;

    let result: ILexemeResult[] = [];
    while (query.length) {
        query = query.replace(/^\s+/, '');

        let lexemes: ILexeme[] = Lexicon.filter(_lexeme =>
            lexeme &&
            _lexeme.when &&
            _lexeme.when.indexOf(lexeme.name) !== -1);

        if (!lexemes.length) {
            lexemes = Lexicon;
        }

        lexeme = lexemes.find(_lexeme => _lexeme.regexp.test(query)) || null;
        if (!lexeme) {
            return { lexemes: result, valid: false, error: query };
        }

        const value = (query.match(lexeme.regexp) || [])[0];
        result.push({ lexeme, value });

        query = query.substring(value.length);
    }

    return { lexemes: result, valid: true };
}