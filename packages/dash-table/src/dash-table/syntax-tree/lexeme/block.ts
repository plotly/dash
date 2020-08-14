import Logger from 'core/Logger';
import {LexemeType, IUnboundedLexeme} from 'core/syntax-tree/lexicon';

export const blockClose: IUnboundedLexeme = {
    nesting: -1,
    regexp: /^\)/,
    type: LexemeType.BlockClose
};

export const blockOpen: IUnboundedLexeme = {
    evaluate: (target, tree) => {
        Logger.trace('evaluate -> ()', target, tree);

        const t = tree as any;

        return t.block.lexeme.evaluate(target, t.block);
    },
    type: LexemeType.BlockOpen,
    nesting: 1,
    subType: '()',
    priority: 1,
    regexp: /^\(/,
    syntaxer: (lexs: any[]) => {
        return Object.assign(
            {
                block: lexs.slice(1, lexs.length - 1)
            },
            lexs[0]
        );
    }
};
