import {expect} from 'chai';
import {describe, it} from 'mocha';
import {handlePatch} from '../src/actions/patch';
import {resolvePropPath} from '../src/utils/propPath';

describe('partial prop reads', () => {
    const data = Object.freeze({
        records: Object.freeze([
            Object.freeze({values: Object.freeze([0, false, '', null])}),
            Object.freeze({values: Object.freeze([42, 'last'])})
        ]),
        empty: Object.freeze([]),
        object: Object.freeze({}),
        '': 'empty key',
        'a.b[0]/c': 'literal',
        中文: 'unicode',
        0: 'string key'
    });

    [
        ['empty path', data, [], data],
        ['object subtree', data, ['records', 0], data.records[0]],
        ['mixed nesting', data, ['records', 1, 'values', 0], 42],
        ['negative indices', data, ['records', -1, 'values', -1], 'last'],
        ['zero', data, ['records', 0, 'values', 0], 0],
        ['false', data, ['records', 0, 'values', 1], false],
        ['empty string', data, ['records', 0, 'values', 2], ''],
        ['null', data, ['records', 0, 'values', 3], null],
        ['empty array', data, ['empty'], data.empty],
        ['empty object', data, ['object'], data.object],
        ['literal key', data, ['a.b[0]/c'], 'literal'],
        ['empty key', data, [''], 'empty key'],
        ['unicode key', data, ['中文'], 'unicode'],
        ['numeric string key', data, ['0'], 'string key'],
        ['missing key', data, ['missing'], undefined],
        ['out-of-range index', data, ['records', 2], undefined],
        ['negative overflow', data, ['records', -3], undefined],
        ['string array index', data, ['records', '0'], undefined],
        ['integer object key', data, [0], undefined],
        [
            'incompatible ancestor',
            data,
            ['records', 0, 'values', 0, 'x'],
            undefined
        ],
        ['unsafe index', data.records, [2 ** 53], undefined]
    ].forEach(([name, value, path, expected]) => {
        it(name, () => {
            expect(resolvePropPath(value, path)).to.equal(expected);
        });
    });

    it('reads own dictionary keys only', () => {
        const value = JSON.parse(
            '{"__proto__":{"value":1},"constructor":2,"hasOwnProperty":3}'
        );
        expect(resolvePropPath(value, ['__proto__', 'value'])).to.equal(1);
        expect(resolvePropPath(value, ['constructor'])).to.equal(2);
        expect(resolvePropPath(value, ['hasOwnProperty'])).to.equal(3);
        expect(resolvePropPath({}, ['toString'])).to.equal(undefined);
        expect(
            resolvePropPath(Object.create({inherited: 1}), ['inherited'])
        ).to.equal(undefined);
    });

    it('matches Patch for an existing negative-index location', () => {
        const location = ['records', -1, 'values', -1];
        const updated = handlePatch(data, {
            operations: [
                {operation: 'Assign', location, params: {value: 'updated'}}
            ]
        });
        expect(resolvePropPath(data, location)).to.equal('last');
        expect(resolvePropPath(updated, location)).to.equal('updated');
    });

    it('does not visit unselected siblings', () => {
        const value = {
            selected: {value: 42},
            get sibling() {
                throw new Error('Unselected sibling was accessed');
            }
        };
        expect(resolvePropPath(value, ['selected', 'value'])).to.equal(42);
    });

    it('handles malformed paths defensively', () => {
        for (const path of ['x', null, {}, [true], [null], [{}]]) {
            expect(resolvePropPath({x: [1]}, path)).to.equal(undefined);
        }
    });
});
