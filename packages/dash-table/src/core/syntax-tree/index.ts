import Logger from 'core/Logger';
import lexer from 'core/syntax-tree/lexer';
import syntaxer, { ISyntaxTree } from 'core/syntax-tree/syntaxer';

export default class SyntaxTree {
    private syntaxTree: ISyntaxTree;

    get isValid() {
        return !!this.syntaxTree;
    }

    constructor(private readonly query: string) {
        try {
            this.syntaxTree = syntaxer(lexer(this.query));
        } catch (_) {
            Logger.debug(`unable to create syntax tree for query=${this.query}`);
        }
    }

    evaluate = (target: any) => {
        if (!this.syntaxTree) {
            const msg = `unable to evaluate target: syntax tree is invalid for query=${this.query}`;

            Logger.error(msg);
            throw new Error(msg);
        }

        const evaluate = this.syntaxTree.lexeme.evaluate;

        return evaluate ?
            evaluate(target, this.syntaxTree) :
            false;
    }

    filter = (targets: any[]) => {
        return targets.filter(this.evaluate);
    }
}