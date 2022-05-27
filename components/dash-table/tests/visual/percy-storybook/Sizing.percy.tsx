import * as R from 'ramda';
import React from 'react';
import {storiesOf} from '@storybook/react';
import DataTable from 'dash-table/dash/DataTable';

const setProps = () => {};

const data = [
    {
        Date: 'July 12th, 2013 - July 25th, 2013',
        Rep: 1,
        Dem: 10,
        Ind: 2,
        Region: 'Northern New York State to the Southern Appalachian Mountains',
        'Election Polling Organization': 'The New York Times'
    },
    {
        Date: 'July 12th, 2013 - August 25th, 2013',
        Rep: -20,
        Dem: 20,
        Ind: 10924,
        Region: 'Canada',
        'Election Polling Organization': 'Pew Research'
    },
    {
        Date: 'July 12th, 2014 - August 25th, 2014',
        Rep: 3.512,
        Dem: 30,
        Ind: 3912,
        Region: 'Southern Vermont',
        'Election Polling Organization': 'The Washington Post'
    }
];

const columns = R.map(
    i => ({name: i, id: i}),
    ['Date', 'Rep', 'Dem', 'Ind', 'Region', 'Election Polling Organization']
);

const props = {
    setProps,
    id: 'table',
    data,
    columns
};

storiesOf('DashTable/Sizing', module).add('all variants', () => (
    <div>
        <div>default styles</div>
        <DataTable {...props} />
        <div>padding</div>
        <DataTable
            {...props}
            css={[
                {
                    selector: '.dash-spreadsheet',
                    rule: 'width: 100%'
                },
                {
                    selector: '.dash-cell[data-dash-column=Region]',
                    rule: 'white-space: normal'
                }
            ]}
            style_data_conditional={[{width: '16.67%'}]}
        />
        <div>single column width by percentage</div>
        <DataTable
            {...props}
            css={[
                {
                    selector: '.dash-spreadsheet',
                    rule: 'width: 100%'
                },
                {
                    selector: '.dash-cell[data-dash-column=Region]',
                    rule: 'white-space: normal'
                }
            ]}
            style_data_conditional={[
                {
                    if: {column_id: 'Region'},
                    width: '50%'
                }
            ]}
        />
        <div>underspecified widths</div>
        <DataTable
            {...props}
            style_data_conditional={[
                {
                    if: {column_id: 'Dem'},
                    width: '100px',
                    min_width: '100px',
                    max_width: '100px'
                },
                {
                    if: {column_id: 'Rep'},
                    width: '100px',
                    min_width: '100px',
                    max_width: '100px'
                },
                {
                    if: {column_id: 'Ind'},
                    width: '100px',
                    min_width: '100px',
                    max_width: '100px'
                }
            ]}
        />
        <div>widths smaller than content</div>
        <DataTable
            {...props}
            css={[
                {
                    selector: '.dash-cell[data-dash-column=Region]',
                    rule: 'white-space: normal'
                }
            ]}
            style_data_conditional={[{width: '100px'}]}
        />
        <div>widths smaller than content (forced)</div>
        <DataTable
            {...props}
            style_data_conditional={[
                {
                    if: {column_id: 'Region'},
                    whiteSpace: 'normal'
                }
            ]}
            style_data={{
                width: '100px',
                min_width: '100px',
                max_width: '100px'
            }}
        />
    </div>
));
