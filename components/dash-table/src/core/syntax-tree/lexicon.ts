import {ILexemeResult} from './lexer';
import {ISyntaxTree} from './syntaxer';

export enum LexemeType {
    BlockClose = 'close-block',
    BlockOpen = 'open-block',
    LogicalOperator = 'logical-operator',
    RelationalOperator = 'relational-operator',
    UnaryOperator = 'unary-operator',
    Expression = 'expression'
}

export interface IUnboundedLexeme {
    evaluate?: (target: any, tree: ISyntaxTree) => boolean;
    present?: (tree: ISyntaxTree) => any;
    resolve?: (target: any, tree: ISyntaxTree) => any;
    subType?: string;
    type: string;
    nesting?: number;
    priority?: number;
    regexp: RegExp;
    regexpFlags?: number;
    regexpMatch?: number;
    syntaxer?: (lexs: any[], pivot: any, pivotIndex: number) => any;
    transform?: (value: any) => any;
}

export interface ILexeme extends IUnboundedLexeme {
    terminal:
        | boolean
        | ((
              lexemes: ILexemeResult[],
              previous: ILexemeResult | undefined
          ) => boolean);
    if:
        | (string | undefined)[]
        | ((
              lexemes: ILexemeResult[],
              previous: ILexemeResult | undefined
          ) => boolean);
}

export function boundLexeme(lexeme: IUnboundedLexeme) {
    return {...lexeme, if: () => false, terminal: false};
}

export type Lexicon = ILexeme[];
