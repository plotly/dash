import {expect} from 'chai';

import {MultiColumnsSyntaxTree} from 'dash-table/syntax-tree';
import {FilterLogicalOperator} from 'dash-table/components/Table/props';

describe('Multi Columns Syntax Tree', () => {
    it('can do single', () => {
        const tree = new MultiColumnsSyntaxTree(
            '{a} >= 3',
            FilterLogicalOperator.And
        );

        expect(tree.isValid).to.equal(true);
    });

    it('can "and"', () => {
        const tree = new MultiColumnsSyntaxTree(
            '{a} >= 3 && {b} is even',
            FilterLogicalOperator.And
        );

        expect(tree.isValid).to.equal(true);
    });

    it('can\'t "and" if operator is "or"', () => {
        const tree = new MultiColumnsSyntaxTree(
            '{a} >= 3 && {b} is even',
            FilterLogicalOperator.Or
        );

        expect(tree.isValid).to.equal(false);
    });

    it('can "or"', () => {
        const tree = new MultiColumnsSyntaxTree(
            '{a} >= 3 || {b} is even',
            FilterLogicalOperator.Or
        );

        expect(tree.isValid).to.equal(true);
    });

    it('can\'t "or" if operator is "and"', () => {
        const tree = new MultiColumnsSyntaxTree(
            '{a} >= 3 || {b} is even',
            FilterLogicalOperator.And
        );

        expect(tree.isValid).to.equal(false);
    });
});
