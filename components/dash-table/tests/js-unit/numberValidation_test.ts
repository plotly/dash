import {expect} from 'chai';

import {ColumnType, INumberColumn} from 'dash-table/components/Table/props';
import {isNully} from 'dash-table/type/null';
import {validate} from 'dash-table/type/number';

const DEFAULT_VALIDATE_SUCCESS = [
    {input: 0, output: 0, name: 'from number (0)'},
    {input: 42, output: 42, name: 'from number (42)'}
];

const ALLOW_NULL_VALIDATE_SUCCESS = [
    {input: NaN, output: null, name: 'from NaN'},
    {input: Infinity, output: null, name: 'from +Infinity'},
    {input: -Infinity, output: null, name: 'from -Infinity'},
    {input: undefined, output: null, name: 'from undefined'},
    {input: null, output: null, name: 'from null'}
];

const DEFAULT_VALIDATE_FAILURE = [
    {input: '42', name: 'from number string'},
    {input: '-42', name: 'from negative number string'},
    {input: '4.242', name: 'from float string'},
    {input: '-4.242', name: 'from negative float string'},
    {input: undefined, name: 'from undefined'},
    {input: null, name: 'from null'},
    {input: NaN, name: 'from NaN'},
    {input: Infinity, name: 'from +Infinity'},
    {input: -Infinity, name: 'from -Infinity'},
    {input: {}, name: 'from object'},
    {input: true, name: 'from boolean'},
    {input: 'abc', name: 'from alphanumeric string'}
];

const ALLOW_NULL_VALIDATE_FAILURE = DEFAULT_VALIDATE_FAILURE.filter(
    entry => !isNully(entry.input)
);

describe('validate number', () => {
    describe('default', () => {
        const options = undefined;

        DEFAULT_VALIDATE_SUCCESS.forEach(entry => {
            it(entry.name, () => {
                const res = validate(entry.input, options);

                expect(res.success).to.equal(true);
                expect(res.value).to.equal(entry.output);
            });
        });

        DEFAULT_VALIDATE_FAILURE.forEach(entry => {
            it(entry.name, () => {
                const res = validate(entry.input, options);

                expect(res.success).to.equal(false);
            });
        });
    });

    describe('allow_null=true', () => {
        const options: INumberColumn = {
            type: ColumnType.Numeric,
            validation: {
                allow_null: true
            }
        };

        ALLOW_NULL_VALIDATE_SUCCESS.forEach(entry => {
            it(entry.name, () => {
                const res = validate(entry.input, options);

                expect(res.success).to.equal(true);
                expect(res.value).to.equal(entry.output);
            });
        });

        DEFAULT_VALIDATE_SUCCESS.forEach(entry => {
            it(entry.name, () => {
                const res = validate(entry.input, options);

                expect(res.success).to.equal(true);
                expect(res.value).to.equal(entry.output);
            });
        });

        ALLOW_NULL_VALIDATE_FAILURE.forEach(entry => {
            it(entry.name, () => {
                const res = validate(entry.input, options);

                expect(res.success).to.equal(false);
            });
        });
    });
});
