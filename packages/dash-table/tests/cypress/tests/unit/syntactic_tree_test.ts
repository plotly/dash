import SyntaxTree from 'core/syntax-tree';

describe('Syntax Tree', () => {
    const data0 = { a: '0', b: '0', c: 0, d: null };
    const data1 = { a: '1', b: '0', c: 1, d: 0 };
    const data2 = { a: '2', b: '1', c: 2, d: '' };
    const data3 = { a: '3', b: '1', c: 3, d: false };

    describe('&& and ||', () => {
        it('can || two conditions', () => {
            const tree = new SyntaxTree('a eq "1" || a eq "2"');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(true);
            expect(tree.evaluate(data2)).to.equal(true);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('can "or" two conditions', () => {
            const tree = new SyntaxTree('a eq "1" or a eq "2"');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(true);
            expect(tree.evaluate(data2)).to.equal(true);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('can && two conditions', () => {
            const tree = new SyntaxTree('a eq "1" && b eq "0"');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(true);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('can "and" two conditions', () => {
            const tree = new SyntaxTree('a eq "1" and b eq "0"');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(true);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('gives priority to && over ||', () => {
            const tree = new SyntaxTree('a eq "1" && a eq "0" || b eq "1"');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(true);
            expect(tree.evaluate(data3)).to.equal(true);
        });

        it('gives priority to "and" over "or"', () => {
            const tree = new SyntaxTree('a eq "1" and a eq "0" or b eq "1"');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(true);
            expect(tree.evaluate(data3)).to.equal(true);
        });
    });

    describe('data types', () => {
        it('can compare numbers', () => {
            const tree = new SyntaxTree('c eq num(1)');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(true);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('can compare string to number and return false', () => {
            const tree = new SyntaxTree('a eq num(1)');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('can compare strings', () => {
            const tree = new SyntaxTree('a eq str(1)');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(true);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('can compare string to number and return false', () => {
            const tree = new SyntaxTree('c eq str(1)');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });
    });

    describe('block', () => {
        it('has priority over && and ||', () => {
            const tree = new SyntaxTree('a eq "1" && (a eq "0" || b eq "1")');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('gives priority over "and" and "or"', () => {
            const tree = new SyntaxTree('a eq "1" and (a eq "0" or b eq "1")');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('can be uselessly nested', () => {
            const tree = new SyntaxTree('((a eq "1" and (((a eq "0" or b eq "1")))))');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('can be nested', () => {
            const tree = new SyntaxTree('a eq "1" and (a eq "0" or (b eq "1" or b eq "0"))');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(true);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });
    });

    describe('unary operators', () => {
        it('can check nil', () => {
            const tree = new SyntaxTree('d is nil');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(true);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('can invert check nil', () => {
            const tree = new SyntaxTree('!(d is nil)');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(true);
            expect(tree.evaluate(data2)).to.equal(true);
            expect(tree.evaluate(data3)).to.equal(true);
        });

        it('can check odd', () => {
            const tree = new SyntaxTree('c is odd');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(true);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(true);
        });

        it('can check odd on string and return false', () => {
            const tree = new SyntaxTree('a is odd');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('can check even', () => {
            const tree = new SyntaxTree('c is even');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(true);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(true);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('can check even on string and return false', () => {
            const tree = new SyntaxTree('a is even');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('can check if string', () => {
            const tree = new SyntaxTree('d is str');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(true);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('can check if number', () => {
            const tree = new SyntaxTree('d is num');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(true);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('can check if bool', () => {
            const tree = new SyntaxTree('d is bool');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(true);
        });

        it('can check if object', () => {
            const tree = new SyntaxTree('d is object');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });
    });

    describe('unary not', () => {
        it('can invert block', () => {
            const tree = new SyntaxTree('!(a eq "1")');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(true);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(true);
            expect(tree.evaluate(data3)).to.equal(true);
        });

        it('can invert block multiple times', () => {
            const tree = new SyntaxTree('!!(a eq "1")');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(true);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });
    });

    describe('logical binary operators', () => {
        it('can do equality (eq) test', () => {
            const tree = new SyntaxTree('a eq "1"');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(true);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('can do equality (=) test', () => {
            const tree = new SyntaxTree('a = "1"');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(true);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('can do difference (ne) test', () => {
            const tree = new SyntaxTree('a ne "1"');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(true);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(true);
            expect(tree.evaluate(data3)).to.equal(true);
        });

        it('can do difference (!=) test', () => {
            const tree = new SyntaxTree('a != "1"');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(true);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(true);
            expect(tree.evaluate(data3)).to.equal(true);
        });

        it('can do greater than (gt) test', () => {
            const tree = new SyntaxTree('a gt "1"');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(true);
            expect(tree.evaluate(data3)).to.equal(true);
        });

        it('can do greater than (>) test', () => {
            const tree = new SyntaxTree('a > "1"');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(true);
            expect(tree.evaluate(data3)).to.equal(true);
        });

        it('can do less than (lt) test', () => {
            const tree = new SyntaxTree('a lt "1"');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(true);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('can do less than (<) test', () => {
            const tree = new SyntaxTree('a < "1"');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(true);
            expect(tree.evaluate(data1)).to.equal(false);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('can do greater or equal to (ge) test', () => {
            const tree = new SyntaxTree('a ge "1"');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(true);
            expect(tree.evaluate(data2)).to.equal(true);
            expect(tree.evaluate(data3)).to.equal(true);
        });

        it('can do greater or equal to (>=) test', () => {
            const tree = new SyntaxTree('a >= "1"');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(false);
            expect(tree.evaluate(data1)).to.equal(true);
            expect(tree.evaluate(data2)).to.equal(true);
            expect(tree.evaluate(data3)).to.equal(true);
        });

        it('can do less or equal to (le) test', () => {
            const tree = new SyntaxTree('a le "1"');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(true);
            expect(tree.evaluate(data1)).to.equal(true);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });

        it('can do less or equal to (<=) test', () => {
            const tree = new SyntaxTree('a <= "1"');

            expect(tree.isValid).to.equal(true);
            expect(tree.evaluate(data0)).to.equal(true);
            expect(tree.evaluate(data1)).to.equal(true);
            expect(tree.evaluate(data2)).to.equal(false);
            expect(tree.evaluate(data3)).to.equal(false);
        });
    });
});