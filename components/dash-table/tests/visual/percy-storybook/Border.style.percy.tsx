import * as R from 'ramda';
import React from 'react';
import {storiesOf} from '@storybook/react';
import DataTable from 'dash-table/dash/DataTable';
import {BORDER_PROPS_DEFAULTS} from './Border.defaults.percy';
import {TableAction, SortMode} from 'dash-table/components/Table/props';

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
    }
];

interface ITest {
    name: string;
    props: any;
}

const ALL_VARIANTS: ITest[] = [{name: 'base', props: {}}, ...OPS_VARIANTS];

const scenarios: ITest[] = [
    {
        name: 'with defaults',
        props: {}
    },
    {
        name: 'with defaults & active cell (1,1)',
        props: {
            active_cell: {
                column: 1,
                column_id: 'b',
                row: 1,
                row_id: null
            }
        }
    },
    {
        name: 'with defaults & active cell (0, 0)',
        props: {
            active_cell: {
                column: 0,
                column_id: 'a',
                row: 0,
                row_id: null
            }
        }
    },
    {
        name: 'with cell style',
        props: {
            style_cell: {
                border: '1px solid hotpink'
            }
        }
    },
    {
        name: 'with data style',
        props: {
            style_data: {
                border: '1px solid hotpink'
            }
        }
    },
    {
        name: 'with header style',
        props: {
            style_header: {
                border: '1px solid hotpink'
            }
        }
    },
    {
        name: 'with filter style',
        props: {
            filter_action: TableAction.Native,
            style_filter: {
                border: '1px solid hotpink'
            }
        }
    },
    {
        name: 'with header / cell (data) style - header wins on cell (data)',
        props: {
            style_cell: {
                border: '1px solid teal'
            },
            style_header: {
                border: '1px solid hotpink'
            }
        }
    },
    {
        name: 'with header / data style - data wins on header',
        props: {
            style_data: {
                border: '1px solid teal'
            },
            style_header: {
                border: '1px solid hotpink'
            }
        }
    },
    {
        name: 'with header / filter / cell (data) style - filter wins on header, filter wins on cell (data)',
        props: {
            filter_action: TableAction.Native,
            style_cell: {
                border: '1px solid teal'
            },
            style_filter: {
                border: '1px solid burlywood'
            },
            style_header: {
                border: '1px solid hotpink'
            }
        }
    },
    {
        name: 'with header / data / cell (filter) style - header wins on cell (filter), data wins on cell (filter)',
        props: {
            filter_action: TableAction.Native,
            style_data: {
                border: '1px solid teal'
            },
            style_cell: {
                border: '1px solid burlywood'
            },
            style_header: {
                border: '1px solid hotpink'
            }
        }
    },
    {
        name: 'with cell (header) / filter / data style - filter wins on cell (header), data wins on filter',
        props: {
            filter_action: TableAction.Native,
            style_data: {
                border: '1px solid teal'
            },
            style_filter: {
                border: '1px solid burlywood'
            },
            style_cell: {
                border: '1px solid hotpink'
            }
        }
    },
    {
        name: 'with data / cell (header, filter) style - data wins on filter',
        props: {
            filter_action: TableAction.Native,
            style_data: {
                border: '1px solid teal'
            },
            style_cell: {
                border: '1px solid hotpink'
            }
        }
    },
    {
        name: 'with header / filter / data style - data wins on filter, filter wins on header',
        props: {
            filter_action: TableAction.Native,
            style_data: {
                border: '1px solid teal'
            },
            style_filter: {
                border: '1px solid burlywood'
            },
            style_header: {
                border: '1px solid hotpink'
            }
        }
    },
    {
        name: 'style as list view',
        props: {
            filter_action: TableAction.Native,
            style_data: {
                border: '1px solid teal'
            },
            style_filter: {
                border: '1px solid burlywood'
            },
            style_header: {
                border: '1px solid hotpink'
            },
            style_as_list_view: true
        }
    },
    {
        name: 'horizontal border between header and first row should be blue',
        props: {
            css: [{selector: 'th', rule: 'border: 1px solid pink'}],
            style_data: {border: '1px solid blue'}
        }
    },
    {
        name: 'horizontal border between header and filter should be purple',
        props: {
            filter_action: TableAction.Native,
            css: [{selector: 'th', rule: 'border: 1px solid pink'}],
            style_filter: {border: '1px solid purple'}
        }
    },
    {
        name: 'horizontal border between active cell (0, 0) and header should be pink',
        props: {
            css: [{selector: 'th', rule: 'border: 1px solid red'}],
            active_cell: {
                column: 0,
                column_id: 'a',
                row: 0,
                row_id: null
            }
        }
    }
];

const ops_scenarios: ITest[] = [
    {
        name: 'data ops do not get styled on conditional column_id',
        props: {
            style_data: {
                border: '1px solid black'
            },
            style_data_conditional: [
                {
                    if: {column_id: 'a'},
                    backgroundColor: 'pink',
                    border: '1px solid red'
                }
            ]
        }
    },
    {
        name: 'data ops do not get styled on conditional column_type',
        props: {
            style_data: {
                border: '1px solid black'
            },
            style_data_conditional: [
                {
                    if: {column_type: 'any'},
                    backgroundColor: 'pink',
                    border: '1px solid red'
                }
            ]
        }
    },
    {
        name: 'data ops get styled on conditional row_index',
        props: {
            style_data: {
                border: '1px solid black'
            },
            style_data_conditional: [
                {
                    if: {row_index: 1},
                    backgroundColor: 'pink',
                    border: '1px solid red'
                }
            ]
        }
    },
    {
        name: 'data ops get styled on conditional filter',
        props: {
            style_data: {
                border: '1px solid black'
            },
            style_data_conditional: [
                {
                    if: {filter_query: '{a} eq 85'},
                    backgroundColor: 'pink',
                    border: '1px solid red'
                }
            ]
        }
    },
    {
        name: 'header ops do not get styled on conditional column_id',
        props: {
            style_header: {
                border: '1px solid black'
            },
            style_header_conditional: [
                {
                    if: {column_id: 'a'},
                    backgroundColor: 'pink',
                    border: '1px solid red'
                }
            ]
        }
    },
    {
        name: 'header ops do not get styled on conditional column_type',
        props: {
            style_header: {
                border: '1px solid black'
            },
            style_header_conditional: [
                {
                    if: {column_type: 'any'},
                    backgroundColor: 'pink',
                    border: '1px solid red'
                }
            ]
        }
    },
    {
        name: 'header ops get styled on conditional header_index',
        props: {
            style_header: {
                border: '1px solid black'
            },
            style_header_conditional: [
                {
                    if: {header_index: 0},
                    backgroundColor: 'pink',
                    border: '1px solid red'
                }
            ]
        }
    },
    {
        name: 'filter ops do not get styled on conditional column_id',
        props: {
            filter_action: TableAction.Native,
            style_filter: {
                border: '1px solid black'
            },
            style_filter_conditional: [
                {
                    if: {column_id: 'a'},
                    backgroundColor: 'pink',
                    border: '1px solid red'
                }
            ]
        }
    },
    {
        name: 'filter ops do not get styled on conditional column_type',
        props: {
            filter_action: TableAction.Native,
            style_filter: {
                border: '1px solid black'
            },
            style_filter_conditional: [
                {
                    if: {column_type: 'any'},
                    backgroundColor: 'pink',
                    border: '1px solid red'
                }
            ]
        }
    },
    {
        name: 'vertical border between column A and column B should be blue',
        props: {
            css: [
                {
                    selector: 'td[data-dash-column="a"]',
                    rule: 'border: 1px solid green'
                }
            ],
            style_data_conditional: [
                {
                    if: {column_id: 'b'},
                    border: '1px solid blue'
                }
            ]
        }
    },
    {
        name: 'horizontal border between header and column A should be dashed blue',
        props: {
            css: [{selector: 'th', rule: 'border: 1px solid red'}],
            style_data_conditional: [
                {
                    if: {column_id: 'a'},
                    border: '1px dashed blue'
                }
            ]
        }
    },
    {
        name: 'vertical border between active cell (0, 0) and cell on column B should be pink',
        props: {
            css: [
                {
                    selector: 'td[data-dash-column="b"]',
                    rule: 'border: 1px solid blue'
                }
            ],
            active_cell: {
                column: 0,
                column_id: 'a',
                row: 0,
                row_id: null
            }
        }
    }
];

storiesOf('DashTable/Border, custom styles', module)
    .add('all variants', () => (
        <div>
            {...R.xprod(scenarios, ALL_VARIANTS).map(([scenario, variant]) => (
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
    ))
    .add('ops variants', () => (
        <div>
            {...R.xprod(ops_scenarios, OPS_VARIANTS).map(
                ([scenario, variant]) => (
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
                )
            )}
        </div>
    ));
