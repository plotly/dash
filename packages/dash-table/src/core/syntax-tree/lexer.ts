import * as R from 'ramda';

import {ILexeme, Lexicon} from 'core/syntax-tree/lexicon';

export interface ILexerResult {
    lexemes: ILexemeResult[];
    valid: boolean;
    error?: string;
}

export interface ILexemeResult {
    lexeme: ILexeme;
    flags?: string;
    value?: string;
}

export default function lexer(lexicon: Lexicon, query: string): ILexerResult {
    const result: ILexemeResult[] = [];

    while (query.length) {
        query = query.replace(/^\s+/, '');

        const previous = result.slice(-1)[0];
        const previousLexeme = previous ? previous.lexeme : null;

        const lexemes: ILexeme[] = lexicon.filter(
            lexeme =>
                lexeme.if &&
                (!Array.isArray(lexeme.if)
                    ? lexeme.if(result, previous)
                    : previousLexeme
                    ? lexeme.if && lexeme.if.indexOf(previousLexeme.type) !== -1
                    : lexeme.if && lexeme.if.indexOf(undefined) !== -1)
        );

        const next = R.find(lexeme => lexeme.regexp.test(query), lexemes);
        if (!next) {
            return {lexemes: result, valid: false, error: query};
        }

        const match = query.match(next.regexp) ?? [];
        const value = match[next.regexpMatch || 0];
        const flags = match[next.regexpFlags || -1];
        result.push({lexeme: next, flags, value});

        query = query.substring(value.length);
    }

    const [terminalPrevious, last] = [undefined, undefined, ...result].slice(
        -2
    );

    const terminal: boolean =
        !last ||
        (typeof last.lexeme.terminal === 'function'
            ? last.lexeme.terminal(result, terminalPrevious)
            : last.lexeme.terminal);

    return {
        lexemes: result,
        valid: terminal
    };
}
