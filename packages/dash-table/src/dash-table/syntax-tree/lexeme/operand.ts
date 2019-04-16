import { LexemeType, IUnboundedLexeme } from 'core/syntax-tree/lexicon';
import { ISyntaxTree } from 'core/syntax-tree/syntaxer';

const FIELD_REGEX = /^{(([^{}\\]|\\.)+)}/;

const getField = (
    value: string
) => value
    .slice(1, value.length - 1)
    .replace(/\\(.)/g, '$1');

const operand: IUnboundedLexeme = {
    present: (tree: ISyntaxTree) => getField(tree.value),
    resolve: (target: any, tree: ISyntaxTree) => {
        if (FIELD_REGEX.test(tree.value)) {
            return target[getField(tree.value)];
        } else {
            throw new Error();
        }
    },
    regexp: FIELD_REGEX,
    subType: 'field',
    type: LexemeType.Operand
};

export default operand;