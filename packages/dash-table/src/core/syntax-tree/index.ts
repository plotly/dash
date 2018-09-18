import Logger from 'core/Logger';
import lexer from 'core/syntax-tree/lexer';
import syntaxer, { ISyntaxerResult } from 'core/syntax-tree/syntaxer';

export default class SyntaxTree {
    private result: ISyntaxerResult;

    get isValid() {
        return this.result.valid;
    }

    private get tree() {
        return this.result.tree;
    }

    constructor(private readonly query: string) {
        this.result = syntaxer(lexer(this.query));
    }

    evaluate = (target: any) => {
        if (!this.isValid || !this.tree) {
            const msg = `unable to evaluate target: syntax tree is invalid for query=${this.query}`;

            Logger.error(msg);
            throw new Error(msg);
        }

        const evaluate = this.tree.lexeme.evaluate;

        return evaluate ?
            evaluate(target, this.tree) :
            false;
    }

    filter = (targets: any[]) => {
        return targets.filter(this.evaluate);
    }
}