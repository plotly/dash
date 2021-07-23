import {expect} from 'chai';

import {ColumnType, IDatetimeColumn} from 'dash-table/components/Table/props';
import {isNully} from 'dash-table/type/null';
import {validate} from 'dash-table/type/date';

const DEFAULT_VALIDATE_SUCCESS = [
    {input: ' 2000 ', output: '2000', name: 'year only'},
    {input: '2125-01\t', output: '2125-01', name: 'year-month'},
    {input: '\t1542-05-16', output: '1542-05-16', name: 'year-month-day'},
    {
        input: '  0369-11-02 15',
        output: '0369-11-02 15',
        name: 'year-month-day hour'
    },
    {
        input: '9999-12-29 03:15 ',
        output: '9999-12-29 03:15',
        name: 'year-month-day hour:minute'
    },
    {
        input: '-9999-01-01 23:59:59 ',
        output: '-9999-01-01 23:59:59',
        name: 'year-month-day hour:minute:second'
    },
    {
        input: '0003-01-01 23:59:59.9999 ',
        output: '0003-01-01 23:59:59.9999',
        name: 'year-month-day hour:minute:second.fraction'
    },
    {input: '93', output: '93', name: 'short year', YY: true},
    {input: '13-1', output: '13-1', name: 'short year-month', YY: true},
    {input: '27-5-7', output: '27-5-7', name: 'short year-month-day', YY: true},
    {
        input: '00-1-1 12:34:56.789',
        output: '00-1-1 12:34:56.789',
        name: 'short year with time',
        YY: true
    },
    {
        input: '2000-01-01T12:00:00',
        output: '2000-01-01T12:00:00',
        name: 'iso8601'
    },
    {
        input: '2000-01-01t12:00:00',
        output: '2000-01-01t12:00:00',
        name: 'iso8601 lower'
    },
    {
        input: '2000-01-01 12:00:00Z',
        output: '2000-01-01 12:00:00Z',
        name: 'with "Z"'
    },
    {
        input: '2000-01-01 12:00:00+0435',
        output: '2000-01-01 12:00:00+0435',
        name: 'with tz offset'
    },
    {
        input: '2000-01-01 12:00:00+04:35',
        output: '2000-01-01 12:00:00+04:35',
        name: 'with tz offset (2)'
    },
    {
        input: '2000-01-01 12:00:00-1159',
        output: '2000-01-01 12:00:00-1159',
        name: 'with tz offset (3)'
    },
    {
        input: '2000-01-01 12:00:00-03:00',
        output: '2000-01-01 12:00:00-03:00',
        name: 'with tz offset (4)'
    },
    {input: '2000-02-29', output: '2000-02-29', name: 'leap year'}
];

const ALLOW_NULL_VALIDATE_SUCCESS = [
    {input: NaN, output: null, name: 'from NaN'},
    {input: Infinity, output: null, name: 'from +Infinity'},
    {input: -Infinity, output: null, name: 'from -Infinity'},
    {input: undefined, output: null, name: 'from undefined'},
    {input: null, output: null, name: 'from null'}
];

const DEFAULT_VALIDATE_FAILURE = [
    {input: 2015, name: 'from 4-digit number year'},
    {input: 15, name: 'from 2-digit number year'},
    {input: 'January 15, 2019', name: 'month name'},
    {input: '2019-jan-01', name: 'short month name'},
    {input: '01-01-2000', name: 'year last'},
    {input: '2000/01/01', name: 'slash separated'},
    {input: '2000 01 01', name: 'space separated'},
    {input: '5-01-01', name: 'one-digit year'},
    {input: '105-01-01', name: 'three-digit year'},
    {input: '02000-01-01', name: 'five-digit year'},
    {input: '2000-13', name: 'bad month'},
    {input: '2000-01-32', name: 'bad day'},
    {input: '2001-02-29', name: 'non-leap-year'},
    {input: '2001-04-31', name: '30-day month'},
    {input: '2000-01-31 25:00', name: 'bad hour'},
    {input: '2000-01-31 22:60', name: 'bad minute'},
    {input: '2000-01-31 22:30:60', name: 'bad second'},
    {input: '2000-01-01+0400', name: 'tz with no time'},
    {input: '2000-01-01Z', name: 'UTC "Z" with no time'},
    {input: '2000-01 12:00', name: 'time with no day'},
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

describe('validate date', () => {
    describe('default', () => {
        const options = undefined;
        const optionsYY: IDatetimeColumn = {
            type: ColumnType.Datetime,
            validation: {
                allow_YY: true
            }
        };

        DEFAULT_VALIDATE_SUCCESS.forEach(entry => {
            it(entry.name, () => {
                let res = validate(entry.input, options);

                if (entry.YY) {
                    expect(res.success).to.equal(false);
                    res = validate(entry.input, optionsYY);
                }

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
        const options: IDatetimeColumn = {
            type: ColumnType.Datetime,
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
                if (!entry.YY) {
                    const res = validate(entry.input, options);

                    expect(res.success).to.equal(true);
                    expect(res.value).to.equal(entry.output);
                }
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
