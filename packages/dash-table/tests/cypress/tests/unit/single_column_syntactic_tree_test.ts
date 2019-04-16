import { SingleColumnSyntaxTree } from 'dash-table/syntax-tree';

describe('Single Column Syntax Tree', () => {
    it('cannot have operand', () => {
        const tree = new SingleColumnSyntaxTree('a', '{a} <= 1');

        expect(tree.isValid).to.equal(false);
    });

    it('cannot have binary dangle', () => {
        const tree = new SingleColumnSyntaxTree('a', '<=');

        expect(tree.isValid).to.equal(false);
    });

    it('cannot be unary + expression', () => {
        const tree = new SingleColumnSyntaxTree('a', 'is prime "a"');

        expect(tree.isValid).to.equal(false);
    });

    it('can be empty', () => {
        const tree = new SingleColumnSyntaxTree('a', '');

        expect(tree.isValid).to.equal(true);
        expect(tree.evaluate({ a: 0 })).to.equal(true);
    });

    it('can be binary + expression', () => {
        const tree = new SingleColumnSyntaxTree('a', '<= 1');

        expect(tree.isValid).to.equal(true);
        expect(tree.evaluate({ a: 0 })).to.equal(true);
        expect(tree.evaluate({ a: 2 })).to.equal(false);

        expect(tree.toQueryString()).to.equal('{a} <= 1');
    });

    it('can be unary', () => {
        const tree = new SingleColumnSyntaxTree('a', 'is prime');

        expect(tree.isValid).to.equal(true);
        expect(tree.evaluate({ a: 5 })).to.equal(true);
        expect(tree.evaluate({ a: 6 })).to.equal(false);

        expect(tree.toQueryString()).to.equal('{a} is prime');
    });

    it('can be expression', () => {
        const tree = new SingleColumnSyntaxTree('a', '1');

        expect(tree.isValid).to.equal(true);
        expect(tree.evaluate({ a: 1 })).to.equal(true);
        expect(tree.evaluate({ a: 2 })).to.equal(false);

        expect(tree.toQueryString()).to.equal('{a} eq 1');
    });
});