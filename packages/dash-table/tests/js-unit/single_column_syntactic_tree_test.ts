import {expect} from 'chai';

import {SingleColumnSyntaxTree} from 'dash-table/syntax-tree';
import {ColumnType} from 'dash-table/components/Table/props';
import {SingleColumnConfig} from 'dash-table/syntax-tree/SingleColumnSyntaxTree';
import {RelationalOperator} from 'dash-table/syntax-tree/lexeme/relational';
import {LexemeType} from 'core/syntax-tree/lexicon';

const COLUMN_ANY: SingleColumnConfig = {
    id: 'a',
    type: ColumnType.Any
};

const COLUMN_DATE: SingleColumnConfig = {
    id: 'a',
    type: ColumnType.Datetime
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
        const tree = new SingleColumnSyntaxTree(
            'is prime "a"',
            COLUMN_UNDEFINED
        );

        expect(tree.isValid).to.equal(false);
    });

    it('can be empty', () => {
        const tree = new SingleColumnSyntaxTree('', COLUMN_UNDEFINED);

        expect(tree.isValid).to.equal(true);
        expect(tree.evaluate({a: 0})).to.equal(true);
    });

    it('can be binary + expression', () => {
        const tree = new SingleColumnSyntaxTree('<= 1', COLUMN_UNDEFINED);

        expect(tree.isValid).to.equal(true);
        expect(tree.evaluate({a: 0})).to.equal(true);
        expect(tree.evaluate({a: 2})).to.equal(false);

        expect(tree.toQueryString()).to.equal('{a} <= 1');
    });

    it('can be unary', () => {
        const tree = new SingleColumnSyntaxTree('is prime', COLUMN_UNDEFINED);

        expect(tree.isValid).to.equal(true);
        expect(tree.evaluate({a: 5})).to.equal(true);
        expect(tree.evaluate({a: 6})).to.equal(false);

        expect(tree.toQueryString()).to.equal('{a} is prime');
    });

    it('can be expression with undefined column type', () => {
        const tree = new SingleColumnSyntaxTree('1', COLUMN_UNDEFINED);

        expect(tree.isValid).to.equal(true);
        expect(tree.evaluate({a: '1'})).to.equal(true);
        expect(tree.evaluate({a: '2'})).to.equal(false);
        expect(tree.evaluate({a: 1})).to.equal(false);
        expect(tree.evaluate({a: 2})).to.equal(false);

        expect(tree.toQueryString()).to.equal('{a} contains 1');
    });

    it('can be expression with numeric column type', () => {
        const tree = new SingleColumnSyntaxTree('1', COLUMN_NUMERIC);

        expect(tree.isValid).to.equal(true);
        expect(tree.evaluate({a: 1})).to.equal(true);
        expect(tree.evaluate({a: 2})).to.equal(false);

        expect(tree.toQueryString()).to.equal('{a} = 1');
    });

    it('can be permissive value expression', () => {
        const tree = new SingleColumnSyntaxTree('Hello world', COLUMN_TEXT);

        expect(tree.isValid).to.equal(true);
        expect(tree.evaluate({a: 'Hello world'})).to.equal(true);
        expect(tree.evaluate({a: 'Helloworld'})).to.equal(false);
        expect(tree.toQueryString()).to.equal('{a} contains "Hello world"');
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
        expect(tree.evaluate({a: 1})).to.equal(true);
        expect(tree.evaluate({a: 2})).to.equal(false);
        expect(tree.evaluate({a: '1'})).to.equal(true);
        expect(tree.evaluate({a: '2'})).to.equal(false);

        expect(tree.toQueryString()).to.equal('{a} contains "1"');
    });

    ['1975', '"1975"'].forEach(value => {
        it(`can be expression '${value}' with datetime column type`, () => {
            const tree = new SingleColumnSyntaxTree(value, COLUMN_DATE);

            expect(tree.evaluate({a: 1975})).to.equal(true);
            expect(tree.evaluate({a: '1975'})).to.equal(true);
            expect(tree.evaluate({a: '1975-01'})).to.equal(true);
            expect(tree.evaluate({a: '1975-01-01'})).to.equal(true);
            expect(tree.evaluate({a: '1975-01-01 01:01:01'})).to.equal(true);

            expect(tree.evaluate({a: 1976})).to.equal(false);
            expect(tree.evaluate({a: '1976'})).to.equal(false);
            expect(tree.evaluate({a: '1976-01'})).to.equal(false);
            expect(tree.evaluate({a: '1976-01-01'})).to.equal(false);
            expect(tree.evaluate({a: '1976-01-01 01:01:01'})).to.equal(false);
        });
    });

    [
        {type: COLUMN_UNDEFINED, name: 'undefined'},
        {type: COLUMN_ANY, name: 'any'},
        {type: COLUMN_TEXT, name: 'text'}
    ].forEach(({type, name}) => {
        it(`returns the correct relational operator lexeme for '${name}' column type`, () => {
            const tree = new SingleColumnSyntaxTree('1', type);
            const structure = tree.toStructure();

            expect(tree.toQueryString()).to.equal('{a} contains 1');
            expect(structure).to.not.equal(null);

            if (structure) {
                expect(structure.value).to.equal(RelationalOperator.Contains);
                expect(structure.subType).to.equal(RelationalOperator.Contains);
                expect(structure.type).to.equal(LexemeType.RelationalOperator);

                expect(structure.left).to.not.equal(null);
                if (structure.left) {
                    expect(structure.left.type).to.equal(LexemeType.Expression);
                    expect(structure.left.subType).to.equal('field');
                    expect(structure.left.value).to.equal('a');
                }

                expect(structure.right).to.not.equal(null);
                if (structure.right) {
                    expect(structure.right.type).to.equal(
                        LexemeType.Expression
                    );
                    expect(structure.right.subType).to.equal('value');
                    expect(structure.right.value).to.equal(1);
                }
            }
        });
    });

    it("returns the correct relational operator lexeme for 'date' column type", () => {
        const tree = new SingleColumnSyntaxTree('1975', COLUMN_DATE);
        const structure = tree.toStructure();

        expect(tree.toQueryString()).to.equal('{a} datestartswith 1975');
        expect(structure).to.not.equal(null);

        if (structure) {
            expect(structure.value).to.equal(RelationalOperator.DateStartsWith);
            expect(structure.subType).to.equal(
                RelationalOperator.DateStartsWith
            );
            expect(structure.type).to.equal(LexemeType.RelationalOperator);

            expect(structure.left).to.not.equal(null);
            if (structure.left) {
                expect(structure.left.type).to.equal(LexemeType.Expression);
                expect(structure.left.subType).to.equal('field');
                expect(structure.left.value).to.equal('a');
            }

            expect(structure.right).to.not.equal(null);
            if (structure.right) {
                expect(structure.right.type).to.equal(LexemeType.Expression);
                expect(structure.right.subType).to.equal('value');
                expect(structure.right.value).to.equal(1975);
            }
        }
    });

    it("returns the correct relational operator lexeme for 'numeric' column type", () => {
        const tree = new SingleColumnSyntaxTree('1', COLUMN_NUMERIC);
        const structure = tree.toStructure();

        expect(tree.toQueryString()).to.equal('{a} = 1');
        expect(structure).to.not.equal(null);

        if (structure) {
            expect(structure.value).to.equal(RelationalOperator.Equal);
            expect(structure.subType).to.equal(RelationalOperator.Equal);
            expect(structure.type).to.equal(LexemeType.RelationalOperator);

            expect(structure.left).to.not.equal(null);
            if (structure.left) {
                expect(structure.left.type).to.equal(LexemeType.Expression);
                expect(structure.left.subType).to.equal('field');
                expect(structure.left.value).to.equal('a');
            }

            expect(structure.right).to.not.equal(null);
            if (structure.right) {
                expect(structure.right.type).to.equal(LexemeType.Expression);
                expect(structure.right.subType).to.equal('value');
                expect(structure.right.value).to.equal(1);
            }
        }
    });
});
