import {expect} from 'chai';

import {
    fieldExpression,
    stringExpression,
    valueExpression
} from 'dash-table/syntax-tree/lexeme/expression';
import {ISyntaxTree} from 'core/syntax-tree/syntaxer';

describe('expression', () => {
    it('resolves field expression', () => {
        expect(!!fieldExpression.resolve).to.equal(true);
        expect(typeof fieldExpression.resolve).to.equal('function');

        if (fieldExpression.resolve) {
            expect(
                fieldExpression.resolve({abc: 3}, {
                    value: '{abc}'
                } as ISyntaxTree)
            ).to.equal(3);
            expect(
                fieldExpression.resolve({'a bc': 3}, {
                    value: '{a bc}'
                } as ISyntaxTree)
            ).to.equal(3);
            expect(
                fieldExpression.resolve({'{abc}': 3}, {
                    value: '{\\{abc\\}}'
                } as ISyntaxTree)
            ).to.equal(3);
            expect(
                fieldExpression.resolve({'"abc"': 3}, {
                    value: '{"abc"}'
                } as ISyntaxTree)
            ).to.equal(3);

            expect(
                fieldExpression.resolve({abc: 3}, {
                    value: '{def}'
                } as ISyntaxTree) === undefined
            ).to.equal(true);
            expect(
                fieldExpression.resolve({abc: 3}, {
                    value: '{a bc}'
                } as ISyntaxTree) === undefined
            ).to.equal(true);
            expect(
                fieldExpression.resolve({abc: 3}, {
                    value: '{"abc"}'
                } as ISyntaxTree) === undefined
            ).to.equal(true);

            expect(
                fieldExpression.resolve.bind(undefined, {}, {
                    value: '3'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                fieldExpression.resolve.bind(undefined, {}, {
                    value: 'abc'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                fieldExpression.resolve.bind(undefined, {}, {
                    value: '{abc'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                fieldExpression.resolve.bind(undefined, {}, {
                    value: 'abc}'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                fieldExpression.resolve.bind(undefined, {}, {
                    value: '}abc{'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                fieldExpression.resolve.bind(undefined, {}, {
                    value: '{{abc}}'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                fieldExpression.resolve.bind(undefined, {}, {
                    value: '"'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                fieldExpression.resolve.bind(undefined, {}, {
                    value: '`'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                fieldExpression.resolve.bind(undefined, {}, {
                    value: "'"
                } as ISyntaxTree)
            ).to.throw();
            expect(
                fieldExpression.resolve.bind(undefined, {}, {
                    value: '{'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                fieldExpression.resolve.bind(undefined, {}, {
                    value: '}'
                } as ISyntaxTree)
            ).to.throw();
        }
    });

    it('resolves string expressions', () => {
        expect(!!stringExpression.resolve).to.equal(true);
        expect(typeof stringExpression.resolve).to.equal('function');

        if (stringExpression.resolve) {
            expect(
                stringExpression.resolve(undefined, {
                    value: "''"
                } as ISyntaxTree)
            ).to.equal('');
            expect(
                stringExpression.resolve(undefined, {
                    value: "'abc'"
                } as ISyntaxTree)
            ).to.equal('abc');
            expect(
                stringExpression.resolve(undefined, {
                    value: '"abc"'
                } as ISyntaxTree)
            ).to.equal('abc');
            expect(
                stringExpression.resolve(undefined, {
                    value: '`abc`'
                } as ISyntaxTree)
            ).to.equal('abc');
            expect(
                stringExpression.resolve(undefined, {
                    value: '"\\""'
                } as ISyntaxTree)
            ).to.equal('"');
            expect(
                stringExpression.resolve(undefined, {
                    value: "'\\''"
                } as ISyntaxTree)
            ).to.equal("'");
            expect(
                stringExpression.resolve(undefined, {
                    value: '`\\``'
                } as ISyntaxTree)
            ).to.equal('`');
            expect(
                stringExpression.resolve(undefined, {
                    value: "'\\\\'"
                } as ISyntaxTree)
            ).to.equal('\\');

            expect(
                stringExpression.resolve.bind(undefined, {}, {
                    value: '3'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                stringExpression.resolve.bind(undefined, {}, {
                    value: 'abc'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                stringExpression.resolve.bind(undefined, {}, {
                    value: '{abc'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                stringExpression.resolve.bind(undefined, {}, {
                    value: 'abc}'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                stringExpression.resolve.bind(undefined, {}, {
                    value: '}abc{'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                stringExpression.resolve.bind(undefined, {}, {
                    value: '{{abc}}'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                stringExpression.resolve.bind(undefined, {}, {
                    value: '"'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                stringExpression.resolve.bind(undefined, {}, {
                    value: '`'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                stringExpression.resolve.bind(undefined, {}, {
                    value: "'"
                } as ISyntaxTree)
            ).to.throw();
            expect(
                stringExpression.resolve.bind(undefined, {}, {
                    value: '{'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                stringExpression.resolve.bind(undefined, {}, {
                    value: '}'
                } as ISyntaxTree)
            ).to.throw();
        }
    });

    it('resolves value expressions', () => {
        expect(!!valueExpression.resolve).to.equal(true);
        expect(typeof valueExpression.resolve).to.equal('function');

        if (valueExpression.resolve) {
            expect(
                valueExpression.resolve(undefined, {
                    value: 'abc'
                } as ISyntaxTree)
            ).to.equal('abc');
            expect(
                valueExpression.resolve(undefined, {
                    value: 'abc   '
                } as ISyntaxTree)
            ).to.equal('abc');
            expect(
                valueExpression.resolve(undefined, {
                    value: 'abc\\ \\ \\ '
                } as ISyntaxTree)
            ).to.equal('abc   ');
            expect(
                valueExpression.resolve(undefined, {
                    value: '\\ \\ \\ abc'
                } as ISyntaxTree)
            ).to.equal('   abc');
            expect(
                valueExpression.resolve(undefined, {
                    value: 'a\\ bc'
                } as ISyntaxTree)
            ).to.equal('a bc');
            expect(
                valueExpression.resolve(undefined, {
                    value: '\\\\'
                } as ISyntaxTree)
            ).to.equal('\\');
            expect(
                valueExpression.resolve(undefined, {
                    value: 'abc\\\\'
                } as ISyntaxTree)
            ).to.equal('abc\\');
            expect(
                valueExpression.resolve(undefined, {
                    value: '123'
                } as ISyntaxTree)
            ).to.equal(123);
            expect(
                valueExpression.resolve(undefined, {
                    value: '123.45'
                } as ISyntaxTree)
            ).to.equal(123.45);
            expect(
                valueExpression.resolve(undefined, {
                    value: '1E6'
                } as ISyntaxTree)
            ).to.equal(1000000);
            expect(
                valueExpression.resolve(undefined, {
                    value: '0x100'
                } as ISyntaxTree)
            ).to.equal(256);
            expect(
                valueExpression.resolve(undefined, {
                    value: '\\{abc'
                } as ISyntaxTree)
            ).to.equal('{abc');
            expect(
                valueExpression.resolve(undefined, {
                    value: 'abc\\}'
                } as ISyntaxTree)
            ).to.equal('abc}');
            expect(
                valueExpression.resolve(undefined, {
                    value: '\\}abc\\{'
                } as ISyntaxTree)
            ).to.equal('}abc{');
            expect(
                valueExpression.resolve(undefined, {
                    value: '\\{\\{abc\\}\\}'
                } as ISyntaxTree)
            ).to.equal('{{abc}}');

            expect(
                valueExpression.resolve.bind(undefined, {}, {
                    value: '{abc'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                valueExpression.resolve.bind(undefined, {}, {
                    value: 'abc}'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                valueExpression.resolve.bind(undefined, {}, {
                    value: '}abc{'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                valueExpression.resolve.bind(undefined, {}, {
                    value: '{{abc}}'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                valueExpression.resolve.bind(undefined, {}, {
                    value: '"'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                valueExpression.resolve.bind(undefined, {}, {
                    value: '`'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                valueExpression.resolve.bind(undefined, {}, {
                    value: "'"
                } as ISyntaxTree)
            ).to.throw();
            expect(
                valueExpression.resolve.bind(undefined, {}, {
                    value: '{'
                } as ISyntaxTree)
            ).to.throw();
            expect(
                valueExpression.resolve.bind(undefined, {}, {
                    value: '}'
                } as ISyntaxTree)
            ).to.throw();
        }
    });
});
