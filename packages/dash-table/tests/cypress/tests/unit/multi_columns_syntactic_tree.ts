import { MultiColumnsSyntaxTree } from 'dash-table/syntax-tree';

describe('Multi Columns Syntax Tree', () => {
    it('can do single', () => {
        const tree = new MultiColumnsSyntaxTree('{a} >= 3');

        expect(tree.isValid).to.equal(true);
    });

    it('can "and"', () => {
        const tree = new MultiColumnsSyntaxTree('{a} >= 3 && {b} is even');

        expect(tree.isValid).to.equal(true);
    });
});