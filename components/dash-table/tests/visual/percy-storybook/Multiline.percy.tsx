import * as R from 'ramda';
import React from 'react';
import {storiesOf} from '@storybook/react';
import DataTable from 'dash-table/dash/DataTable';
import {BORDER_PROPS_DEFAULTS} from './Border.defaults.percy';
import {SortMode} from 'dash-table/components/Table/props';

const OPS_VARIANTS: ITest[] = [
    {
        name: 'with ops',
        props: {row_deletable: true, row_selectable: SortMode.Single}
    },
    {
        name: 'fixed columns',
        props: {
            fixed_columns: {headers: true},
            row_deletable: true,
            row_selectable: SortMode.Single
        }
    },
    {
        name: 'fixed rows',
        props: {
            fixed_rows: {headers: true},
            row_deletable: true,
            row_selectable: SortMode.Single
        }
    },
    {
        name: 'fixed columns & rows',
        props: {
            fixed_columns: {headers: true},
            fixed_rows: {headers: true},
            row_deletable: true,
            row_selectable: SortMode.Single
        }
    },
    {
        name: 'fixed columns & rows inside fragments',
        props: {
            fixed_columns: {headers: true, data: 1},
            fixed_rows: {headers: true, data: 1},
            row_deletable: true,
            row_selectable: SortMode.Single
        }
    },
    {
        name: 'fixed columns & rows inside fragments (no ops)',
        props: {
            fixed_columns: {headers: true, data: 1},
            fixed_rows: {headers: true, data: 1}
        }
    }
];

interface ITest {
    name: string;
    props: any;
}

const ALL_VARIANTS: ITest[] = [{name: 'base', props: {}}, ...OPS_VARIANTS];

const scenarios: ITest[] = [
    {
        name: 'wrapped text',
        props: {
            columns: [
                {id: 'Date', name: 'Date'},
                {
                    id: 'Election Polling Organization',
                    name: 'Election Polling Organization'
                },
                {id: 'Rep', name: 'Rep'},
                {id: 'Dem', name: 'Dem'},
                {id: 'Ind', name: 'Ind'},
                {id: 'Region', name: 'Region'}
            ],
            data: [
                {
                    Date: 'July 12th, 2013 - July 25th, 2013',
                    'Election Polling Organization': 'The New York Times',
                    Rep: 1,
                    Dem: 10,
                    Ind: 2,
                    Region: 'Northern New York State to the Southern Appalachian Mountains'
                },
                {
                    Date: 'July 12th, 2013 - August 25th, 2013',
                    'Election Polling Organization': 'Pew Research',
                    Rep: -20,
                    Dem: 20,
                    Ind: 10924,
                    Region: 'Canada'
                },
                {
                    Date: 'July 12th, 2014 - August 25th, 2014',
                    'Election Polling Organization': 'The Washington Post',
                    Rep: 3.512,
                    Dem: 30,
                    Ind: 3912,
                    Region: 'Southern Vermont'
                }
            ],
            style_table: {maxWidth: '500px', minWidth: '500px', width: '500px'},
            style_data: {whiteSpace: 'normal', height: 'auto'}
        }
    }
];

const tests = R.xprod(scenarios, ALL_VARIANTS);

storiesOf('DashTable/Multiline', module).add('all variants', () => (
    <div>
        {...tests.map(([scenario, variant]) => (
            <div>
                <div>{`${scenario.name} (${variant.name})`}</div>
                <DataTable
                    {...R.mergeAll([
                        BORDER_PROPS_DEFAULTS,
                        variant.props,
                        scenario.props
                    ])}
                />
            </div>
        ))}
    </div>
));
