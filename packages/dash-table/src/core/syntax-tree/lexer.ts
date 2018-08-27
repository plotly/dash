import Lexicon, { ILexeme } from 'core/syntax-tree/lexicon';

export interface ILexerResult {
    lexeme: ILexeme;
    value?: string;
}

export default function lexer(query: string): ILexerResult[] {
    let lexeme: ILexeme | null = null;

    let res: ILexerResult[] = [];
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
            throw new Error('no matching lexeme');
        }

        const value = (query.match(lexeme.regexp) || [])[0];
        res.push({ lexeme, value });

        query = query.substring(value.length);
    }

    return res;
}