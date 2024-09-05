import {expect} from 'chai';

import {ColumnType, ITextColumn} from 'dash-table/components/Table/props';
import {coerce} from 'dash-table/type/text';

const DEFAULT_COERCE_SUCCESS = [
    {input: 42, output: '42', name: 'from number'},
    {input: true, output: 'true', name: 'from boolean'},
    {input: 'abc', output: 'abc', name: 'from string'},
    {input: [], output: '[]', name: 'from array'},
    {input: {}, output: '{}', name: 'from object'}
];

const DEFAULT_COERCE_FAILURE = [
    {input: NaN, name: 'from NaN'},
    {input: Infinity, name: 'from +Infinity'},
    {input: -Infinity, name: 'from -Infinity'},
    {input: undefined, name: 'from undefined'},
    {input: null, name: 'from null'}
];

describe('coerce to string', () => {
    describe('default', () => {
        const options = undefined;

        DEFAULT_COERCE_SUCCESS.forEach(entry => {
            it(entry.name, () => {
                const res = coerce(entry.input, options);

                expect(res.success).to.equal(true);
                expect(res.value).to.equal(entry.output);
            });
        });

        DEFAULT_COERCE_FAILURE.forEach(entry => {
            it(entry.name, () => {
                const res = coerce(entry.input, options);

                expect(res.success).to.equal(false);
            });
        });
    });

    describe('allow_null=true', () => {
        const options: ITextColumn = {
            type: ColumnType.Text,
            validation: {
                allow_null: true
            }
        };

        DEFAULT_COERCE_SUCCESS.forEach(entry => {
            it(entry.name, () => {
                const res = coerce(entry.input, options);

                expect(res.success).to.equal(true);
                expect(res.value).to.equal(entry.output);
            });
        });

        DEFAULT_COERCE_FAILURE.forEach(entry => {
            it(entry.name, () => {
                const res = coerce(entry.input, options);

                expect(res.success).to.equal(true);
            });
        });
    });
});
