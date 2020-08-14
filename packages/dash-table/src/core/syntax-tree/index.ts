import * as R from 'ramda';

import Logger from 'core/Logger';
import lexer, {ILexerResult} from 'core/syntax-tree/lexer';
import syntaxer, {
    ISyntaxerResult,
    ISyntaxTree
} from 'core/syntax-tree/syntaxer';
import {Lexicon} from './lexicon';

interface IStructure {
    subType?: string;
    type: string;
    value: any;

    block?: IStructure;
    left?: IStructure;
    right?: IStructure;
}

function toStructure(tree: ISyntaxTree): IStructure {
    const {block, left, lexeme, right, value} = tree;

    const res: IStructure = {
        subType: lexeme.subType,
        type: lexeme.type,
        value: lexeme.present ? lexeme.present(tree) : value
    };

    if (block) {
        res.block = toStructure(block);
    }

    if (left) {
        res.left = toStructure(left);
    }

    if (right) {
        res.right = toStructure(right);
    }

    return res;
}

export default class SyntaxTree {
    protected lexerResult: ILexerResult;
    protected syntaxerResult: ISyntaxerResult;

    get isValid() {
        return this.syntaxerResult.valid;
    }

    private get tree() {
        return this.syntaxerResult.tree;
    }

    constructor(
        public readonly lexicon: Lexicon,
        public readonly query: string,
        postProcessor: (res: ILexerResult) => ILexerResult = res => res
    ) {
        this.lexerResult = postProcessor(lexer(this.lexicon, this.query));
        this.syntaxerResult = syntaxer(this.lexerResult);
    }

    evaluate = (target: any) => {
        if (!this.isValid) {
            const msg = `DataTable filtering syntax is invalid for query: ${this.query}`;

            Logger.error(msg);
            throw new Error(msg);
        }

        return this.tree && this.tree.lexeme && this.tree.lexeme.evaluate
            ? this.tree.lexeme.evaluate(target, this.tree)
            : true;
    };

    filter = (targets: any[]) => {
        return targets.filter(this.evaluate);
    };

    toQueryString() {
        return this.lexerResult.valid
            ? R.map(
                  l =>
                      l.lexeme.transform
                          ? l.lexeme.transform(l.value)
                          : l.value,
                  this.lexerResult.lexemes
              ).join(' ')
            : '';
    }

    toStructure() {
        if (!this.isValid || !this.syntaxerResult.tree) {
            return null;
        }

        return toStructure(this.syntaxerResult.tree);
    }
}
