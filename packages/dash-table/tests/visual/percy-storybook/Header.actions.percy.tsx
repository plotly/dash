import * as R from 'ramda';
import React from 'react';
import { storiesOf } from '@storybook/react';
import DataTable from 'dash-table/dash/DataTable';

const setProps = () => { };

const DATA_BASE = R.map(i => ({
    year: i,
    montreal: i * 10,
    toronto: i * 100,
    ottawa: i * -1,
    vancouver: i * -10,
    temp: i * -100,
    humidity: i * 0.1
}), R.range(0, 10));

const COLUMNS_BASE = [
    { name: ['Year', ''], id: 'year' },
    { name: ['City', 'Montreal'], id: 'montreal' },
    { name: ['City', 'Toronto'], id: 'toronto' },
    { name: ['City', 'Ottawa'], id: 'ottawa' },
    { name: ['City', 'Vancouver'], id: 'vancouver' },
    { name: ['Climate', 'Temperature'], id: 'temp' },
    { name: ['Climate', 'Humidity'], id: 'humidity' }
];

interface ITest {
    name: string;
    props: any;
}

const DEFAULT_PROPS = {
    id: 'clear-header',
    data: DATA_BASE,
    setProps
};

const variants: ITest[] = [
    {
        name: 'base',
        props: {}
    }, {
        name: 'merged',
        props: {
            merge_duplicate_headers: true
        }
    }
];

const scenarios: ITest[] = [
    {
        name: 'clearable',
        props: {
            columns: R.map(c => R.mergeRight(c, {
                clearable: true
            }), COLUMNS_BASE)
        }
    }, {
        name: 'clearable (top-city, bottom-climate)',
        props: {
            columns: R.map((c: any) => {
                const firstName = c.name[0];

                if (firstName === 'City') {
                    return R.mergeRight(c, {
                        clearable: [true, false]
                    });
                } else if (firstName === 'Climate') {
                    return R.mergeRight(c, {
                        clearable: [false, true]
                    });

                } else {
                    return c;
                }
            }, COLUMNS_BASE)
        }
    }, {
        name: 'deletable',
        props: {
            columns: R.map(c => R.mergeRight(c, {
                deletable: true
            }), COLUMNS_BASE)
        }
    }, {
        name: 'deletable (top-city, bottom-climate)',
        props: {
            columns: R.map((c: any) => {
                const firstName = c.name[0];

                if (firstName === 'City') {
                    return R.mergeRight(c, {
                        deletable: [true, false]
                    });
                } else if (firstName === 'Climate') {
                    return R.mergeRight(c, {
                        deletable: [false, true]
                    });

                } else {
                    return c;
                }
            }, COLUMNS_BASE)
        }
    }, {
        name: 'clearable+deletable',
        props: {
            columns: R.map(c => R.mergeRight(c, {
                clearable: true,
                deletable: true
            }), COLUMNS_BASE)
        }
    }
];

const tests = R.xprod(scenarios, variants);

R.reduce(
    (chain, [scenario, variant]) => chain.add(`${scenario.name} (${variant.name})`, () => (<DataTable
        {...R.mergeAll([
            DEFAULT_PROPS,
            variant.props,
            scenario.props
        ])}
    />)),
    storiesOf(`DashTable/Headers, actions`, module),
    tests
);