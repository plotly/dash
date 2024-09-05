import parser from 'papaparse';
import * as R from 'ramda';
import React from 'react';
import {storiesOf} from '@storybook/react';

import DataTable from 'dash-table/dash/DataTable';

import dataset from './../../assets/gapminder.csv';

const result = parser.parse(dataset, {delimiter: ',', header: true});

const getColumns = () =>
    R.addIndex(R.map)(
        (id, index) => ({
            name: [
                Math.floor(index / 4).toString(),
                Math.floor(index / 2).toString(),
                id
            ],
            id
        }),
        result.meta.fields as any
    );

interface ITest {
    name: string;
    props: any;
}

const DEFAULT_PROPS = {
    id: 'table',
    data: result.data.slice(0, 5)
};

const variants: ITest[] = [
    {name: 'merged', props: {merge_duplicate_headers: true}},
    {name: 'unmerged', props: {merge_duplicate_headers: false}}
];

const scenarios: ITest[] = [
    {
        name: 'default (all)',
        props: {
            columns: getColumns().map((c: any) => {
                c.hideable = true;

                return c;
            })
        }
    },
    {
        name: 'explicit bottom row',
        props: {
            columns: getColumns().map((c: any) => {
                c.hideable = [false, false, true];

                return c;
            })
        }
    },
    {
        name: 'explicit middle row',
        props: {
            columns: getColumns().map((c: any) => {
                c.hideable = [false, true, false];

                return c;
            })
        }
    },
    {
        name: 'explicit top row',
        props: {
            columns: getColumns().map((c: any) => {
                c.hideable = [true, false, false];

                return c;
            })
        }
    },
    {
        name: 'some non-hideable top rows',
        props: {
            columns: getColumns().map((c: any, i) => {
                c.hideable = [true, false, false];
                if (i % 8 === 0) {
                    c.hideable = false;
                }

                return c;
            })
        }
    },
    {
        name: 'some non-hideable middle rows',
        props: {
            columns: getColumns().map((c: any, i) => {
                c.hideable = [false, true, false];
                if (i % 4 === 0) {
                    c.hideable = false;
                }

                return c;
            })
        }
    },
    {
        name: 'some non-hideable bottom rows',
        props: {
            columns: getColumns().map((c: any, i) => {
                c.hideable = [false, false, true];
                if (i % 2 === 0) {
                    c.hideable = false;
                }

                return c;
            })
        }
    },
    {
        name: 'some hideable top rows',
        props: {
            columns: getColumns().map((c: any, i) => {
                c.hideable = false;
                if (i % 8 === 0) {
                    c.hideable = [true, false, false];
                }

                return c;
            })
        }
    },
    {
        name: 'some hideable middle rows',
        props: {
            columns: getColumns().map((c: any, i) => {
                c.hideable = false;
                if (i % 4 === 0) {
                    c.hideable = [false, true, false];
                }

                return c;
            })
        }
    },
    {
        name: 'some hideable bottom rows',
        props: {
            columns: getColumns().map((c: any, i) => {
                c.hideable = false;
                if (i % 2 === 0) {
                    c.hideable = [false, false, true];
                }

                return c;
            })
        }
    }
];

const tests = R.xprod(scenarios, variants);

storiesOf('DashTable/Hideable Columns', module).add('all variants', () => (
    <div>
        {...tests.map(([scenario, variant]) => (
            <div>
                <div>{`${scenario.name} (${variant.name})`}</div>
                <DataTable
                    {...R.mergeAll([
                        DEFAULT_PROPS,
                        variant.props,
                        scenario.props
                    ])}
                />
            </div>
        ))}
    </div>
));
