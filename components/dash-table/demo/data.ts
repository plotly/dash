/* eslint no-magic-numbers: 0 */
import * as R from 'ramda';
import {ColumnType} from 'dash-table/components/Table/props';

const N_DATA = 100000;

export interface IDataMock {
    columns: any[];
    data: any[];
}

export const generateMockData = (rows: number) =>
    unpackIntoColumnsAndData([
        {
            id: 'rows',
            type: ColumnType.Numeric,
            editable: false,
            data: gendata(i => i, rows)
        },

        {
            id: 'ccc',
            name: ['City', 'Canada', 'Toronto'],
            type: ColumnType.Numeric,
            data: gendata(i => i, rows)
        },

        {
            id: 'ddd',
            name: ['City', 'Canada', 'Montréal'],
            type: ColumnType.Numeric,
            data: gendata(i => i * 100, rows)
        },

        {
            id: 'eee',
            name: ['City', 'America', 'New York City'],
            type: ColumnType.Numeric,
            data: gendata(i => i, rows)
        },

        {
            id: 'fff',
            name: ['City', 'America', 'Boston'],
            type: ColumnType.Numeric,
            data: gendata(i => i + 1, rows)
        },

        {
            id: 'ggg',
            name: ['City', 'France', 'Paris'],
            type: ColumnType.Numeric,
            editable: true,
            data: gendata(i => i * 10, rows)
        },

        {
            id: 'bbb',
            name: ['', 'Weather', 'Climate'],
            type: ColumnType.Text,
            presentation: 'dropdown',
            data: gendata(
                i => ['Humid', 'Wet', 'Snowy', 'Tropical Beaches'][i % 4],
                rows
            )
        },

        {
            id: 'bbb-readonly',
            name: ['', 'Weather', 'Climate-RO'],
            type: ColumnType.Text,
            presentation: 'dropdown',
            editable: false,
            data: gendata(
                i => ['Humid', 'Wet', 'Snowy', 'Tropical Beaches'][i % 4],
                rows
            )
        },

        {
            id: 'aaa',
            name: ['', 'Weather', 'Temperature'],
            type: ColumnType.Numeric,
            data: gendata(i => i + 1, rows)
        },

        {
            id: 'aaa-readonly',
            name: ['', 'Weather', 'Temperature-RO'],
            type: ColumnType.Numeric,
            presentation: 'dropdown',
            editable: false,
            data: gendata(i => i + 1, rows)
        }
    ]);

export const generateMarkdownMockData = (rows: number) =>
    unpackIntoColumnsAndData([
        {
            id: 'markdown-headers',
            name: ['', 'Headers'],
            presentation: 'markdown',
            data: gendata(i => '#'.repeat(i % 6) + ' row ' + i, rows)
        },
        {
            id: 'markdown-italics',
            name: ['Emphasis', 'Italics'],
            presentation: 'markdown',
            data: gendata(i => (i % 2 ? '*' + i + '*' : '_' + i + '_'), rows)
        },
        {
            id: 'markdown-links',
            name: ['', 'Links'],
            presentation: 'markdown',
            data: gendata(
                i =>
                    '[Learn about ' +
                    i +
                    '](http://en.wikipedia.org/wiki/' +
                    i +
                    ')',
                rows
            )
        },
        {
            id: 'markdown-lists',
            name: ['', 'Lists'],
            presentation: 'markdown',
            data: gendata(
                i =>
                    [
                        '1. Row number ' + i,
                        '    - subitem ' + i,
                        '      - subsubitem ' + i,
                        '    - subitem two ' + i,
                        '2. Next row ' + (i + 1)
                    ].join('\n'),
                rows
            )
        },
        {
            id: 'markdown-tables',
            name: ['', 'Tables'],
            presentation: 'markdown',
            data: gendata(
                i =>
                    ['Current | Next', '--- | ---', i + ' | ' + (i + 1)].join(
                        '\n'
                    ),
                rows
            )
        },
        {
            id: 'markdown-quotes',
            name: ['', 'Quotes'],
            presentation: 'markdown',
            data: gendata(i => '> A quote for row number ' + i, rows)
        },
        {
            id: 'markdown-inline-code',
            name: ['', 'Inline code'],
            presentation: 'markdown',
            data: gendata(i => 'This is row `' + i + '` in this table.', rows)
        },
        {
            id: 'markdown-code-blocks',
            name: ['', 'Code blocks'],
            presentation: 'markdown',
            data: gendata(
                i =>
                    [
                        '```python',
                        'def hello_table(i=' + i + '):',
                        '  print("hello, " + i)'
                    ].join('\n'),
                rows
            )
        },
        {
            id: 'markdown-images',
            name: ['', 'Images'],
            presentation: 'markdown',
            data: gendata(
                i =>
                    '![image ' +
                    i +
                    ' alt text](https://dash.plotly.com/assets/images/logo.png)',
                rows
            )
        }
    ]);

export const generateMixedMarkdownMockData = (rows: number) =>
    unpackIntoColumnsAndData([
        {
            id: 'not-markdown-column',
            name: ['Not Markdown'],
            editable: true,
            data: gendata(_ => 'this is not a markdown cell', rows)
        },
        {
            id: 'markdown-column',
            name: ['Markdown'],
            type: ColumnType.Text,
            presentation: 'markdown',
            data: gendata(
                i =>
                    [
                        '```javascript',
                        ...(i % 2 === 0
                            ? ['console.warn("this is a markdown cell")']
                            : [
                                  'console.log("logging things")',
                                  'console.warn("this is a markdown cell")'
                              ]),
                        '```'
                    ].join('\n'),
                rows
            )
        },
        {
            id: 'also-not-markdown-column',
            name: ['Also Not Markdown'],
            editable: false,
            data: gendata(i => i, rows)
        },
        {
            id: 'also-also-not-markdown-column',
            name: ['Also Also Not Markdown'],
            editable: true,
            data: gendata(_ => 'this is also also not a markdown cell', rows)
        }
    ]);

export const generateSpaceMockData = (rows: number) =>
    unpackIntoColumnsAndData([
        {
            id: 'rows',
            type: ColumnType.Numeric,
            editable: false,
            data: gendata(i => i, rows)
        },

        {
            id: 'c cc',
            name: ['City', 'Canada', 'Toronto'],
            type: ColumnType.Numeric,
            data: gendata(i => i, rows)
        },

        {
            id: 'd:dd',
            name: ['City', 'Canada', 'Montréal'],
            type: ColumnType.Numeric,
            data: gendata(i => i * 100, rows)
        },

        {
            id: 'e-ee',
            name: ['City', 'America', 'New York City'],
            type: ColumnType.Numeric,
            data: gendata(i => i, rows)
        },

        {
            id: 'f_ff',
            name: ['City', 'America', 'Boston'],
            type: ColumnType.Numeric,
            data: gendata(i => i + 1, rows)
        },

        {
            id: 'g.gg',
            name: ['City', 'France', 'Paris'],
            type: ColumnType.Numeric,
            editable: true,
            data: gendata(i => i * 10, rows)
        },

        {
            id: 'b+bb',
            name: ['', 'Weather', 'Climate'],
            type: ColumnType.Text,
            presentation: 'dropdown',
            data: gendata(
                i => ['Humid', 'Wet', 'Snowy', 'Tropical Beaches'][i % 4],
                rows
            )
        }
    ]);

export const mockDataSimple = (rows: number) =>
    unpackIntoColumnsAndData([
        {
            id: 'aaa',
            name: 'Temperature',
            type: ColumnType.Numeric,
            data: gendata(i => i + 1, rows)
        },

        {
            id: 'bbb',
            name: 'Climate',
            type: ColumnType.Text,
            presentation: 'dropdown',
            data: gendata(
                i => ['Humid', 'Wet', 'Snowy', 'Tropical Beaches'][i % 4],
                rows
            )
        }
    ]);

export const miniData = unpackIntoColumnsAndData([
    {
        id: 'aaa',
        name: 'cheese',
        data: [1, 2, 3]
    },
    {
        id: 'bbb',
        name: 'tomato',
        data: [3, 2, 1]
    }
]);

function unpackIntoColumnsAndData(columns: any[]): IDataMock {
    const mocked: any = {columns: [], data: []};

    columns.forEach(col => {
        col.data.forEach((v: any, i: number) => {
            if (!mocked.data[i]) {
                mocked.data[i] = {};
            }
            mocked.data[i][col.id] = v;
        });
        mocked.columns.push(R.dissoc('data', col));
    });
    return mocked;
}

function gendata(func: (i: number) => any, ndata = N_DATA) {
    return R.range(1, ndata).map(func);
}
