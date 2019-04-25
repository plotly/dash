import { SingleColumnSyntaxTree } from 'dash-table/syntax-tree';
import { ColumnType } from 'dash-table/components/Table/props';
import { SingleColumnConfig } from 'dash-table/syntax-tree/SingleColumnSyntaxTree';

const COLUMN_ANY: SingleColumnConfig = {
    id: 'a',
    type: ColumnType.Any
};

const COLUMN_NUMERIC: SingleColumnConfig = {
    id: 'a',
    type: ColumnType.Numeric
};

const COLUMN_TEXT: SingleColumnConfig = {
    id: 'a',
    type: ColumnType.Text
};

const COLUMN_UNDEFINED: SingleColumnConfig = {
    id: 'a',
    type: undefined
};

describe('Single Column Syntax Tree', () => {
    it('cannot have operand', () => {
        const tree = new SingleColumnSyntaxTree('{a} <= 1', COLUMN_UNDEFINED);

        expect(tree.isValid).to.equal(false);
    });

    it('cannot have binary dangle', () => {
        const tree = new SingleColumnSyntaxTree('<=', COLUMN_UNDEFINED);

        expect(tree.isValid).to.equal(false);
    });

    it('cannot be unary + expression', () => {
        const tree = new SingleColumnSyntaxTree('is prime "a"', COLUMN_UNDEFINED);

        expect(tree.isValid).to.equal(false);
    });

    it('can be empty', () => {
        const tree = new SingleColumnSyntaxTree('', COLUMN_UNDEFINED);

        expect(tree.isValid).to.equal(true);
        expect(tree.evaluate({ a: 0 })).to.equal(true);
    });

    it('can be binary + expression', () => {
        const tree = new SingleColumnSyntaxTree('<= 1', COLUMN_UNDEFINED);

        expect(tree.isValid).to.equal(true);
        expect(tree.evaluate({ a: 0 })).to.equal(true);
        expect(tree.evaluate({ a: 2 })).to.equal(false);

        expect(tree.toQueryString()).to.equal('{a} <= 1');
    });

    it('can be unary', () => {
        const tree = new SingleColumnSyntaxTree('is prime', COLUMN_UNDEFINED);

        expect(tree.isValid).to.equal(true);
        expect(tree.evaluate({ a: 5 })).to.equal(true);
        expect(tree.evaluate({ a: 6 })).to.equal(false);

        expect(tree.toQueryString()).to.equal('{a} is prime');
    });

    it('can be expression with undefined column type', () => {
        const tree = new SingleColumnSyntaxTree('1', COLUMN_UNDEFINED);

        expect(tree.isValid).to.equal(true);
        expect(tree.evaluate({ a: 1 })).to.equal(true);
        expect(tree.evaluate({ a: 2 })).to.equal(false);

        expect(tree.toQueryString()).to.equal('{a} contains 1');
    });

    it('can be expression with numeric column type', () => {
        const tree = new SingleColumnSyntaxTree('1', COLUMN_NUMERIC);

        expect(tree.isValid).to.equal(true);
        expect(tree.evaluate({ a: 1 })).to.equal(true);
        expect(tree.evaluate({ a: 2 })).to.equal(false);

        expect(tree.toQueryString()).to.equal('{a} = 1');
    });

    it('`undefined` column type can use `contains`', () => {
        const tree = new SingleColumnSyntaxTree('contains 1', COLUMN_UNDEFINED);

        expect(tree.isValid).to.equal(true);
    });

    it('`any` column type can use `contains`', () => {
        const tree = new SingleColumnSyntaxTree('contains 1', COLUMN_ANY);

        expect(tree.isValid).to.equal(true);
    });

    it('`numeric` column type can use `contains`', () => {
        const tree = new SingleColumnSyntaxTree('contains 1', COLUMN_NUMERIC);

        expect(tree.isValid).to.equal(true);
    });

    it('can be expression with text column type', () => {
        const tree = new SingleColumnSyntaxTree('"1"', COLUMN_TEXT);

        expect(tree.isValid).to.equal(true);
        expect(tree.evaluate({ a: '1' })).to.equal(true);
        expect(tree.evaluate({ a: '2' })).to.equal(false);

        expect(tree.toQueryString()).to.equal('{a} contains "1"');
    });
});