import {ColumnType, Presentation} from 'dash-table/components/Table/props';

export default [
    {
        name: 'fixed rows -> dropdown',
        props: {
            id: 'table',
            columns: [
                {
                    name: 'Column 1',
                    id: 'column-1',
                    type: ColumnType.Text,
                    presentation: Presentation.Dropdown
                }
            ],
            dropdown: {
                'column-1': {
                    options: [
                        {label: 'Montréal', value: 'mtl'},
                        {label: 'San Francisco', value: 'sf'}
                    ]
                }
            },
            data: [
                {'column-1': 'mtl'},
                {'column-1': 'sf'},
                {'column-1': 'mtl'},
                {'column-1': 'boston'}
            ],
            fixed_rows: {headers: true},
            editable: true,
            css: [
                {
                    selector: '.dash-spreadsheet.dash-freeze-top',
                    rule: 'height: 110px;'
                }
            ]
        }
    },
    {
        name: 'minimal',
        props: {
            id: 'table'
        }
    },

    {
        name: 'minimal-data',
        props: {
            data: [
                {
                    x: 1
                }
            ],
            id: 'table'
        }
    },

    {
        name: 'minimal-columns',
        props: {
            columns: [
                {
                    name: 'column 1',
                    id: 'column-1'
                }
            ],
            id: 'table'
        }
    },

    {
        name: 'simple-columns-and-data',
        props: {
            columns: [
                {
                    name: 'Column 1',
                    id: 'column-1'
                },
                {
                    name: 'Column 2',
                    id: 'column-2'
                }
            ],
            data: [
                {'column-1': 1, 'column-2': 4},
                {'column-1': 2, 'column-2': 4}
            ],
            id: 'table'
        }
    },

    {
        name: 'extra-columns',
        props: {
            columns: [
                {
                    name: 'Column 1',
                    id: 'column-1'
                },
                {
                    name: 'Column 2',
                    id: 'column-2'
                },
                {
                    name: 'Column 3',
                    id: 'column-3'
                }
            ],
            data: [
                {'column-1': 1, 'column-2': 2},
                {'column-1': 10, 'column-2': 20}
            ],
            id: 'table'
        }
    },

    {
        name: 'extra-rows',
        props: {
            columns: [
                {
                    name: 'Column 1',
                    id: 'column-1'
                }
            ],
            data: [
                {'column-1': 3, 'column-2': 10},
                {'column-1': 30, 'column-2': 20}
            ],
            id: 'table'
        }
    },

    {
        name: 'dropdown',
        props: {
            columns: [
                {
                    name: 'Column 1',
                    id: 'column-1',
                    type: ColumnType.Text,
                    presentation: Presentation.Dropdown
                }
            ],
            dropdown: {
                'column-1': {
                    options: [
                        {label: 'Montréal', value: 'mtl'},
                        {label: 'San Francisco', value: 'sf'}
                    ]
                }
            },
            data: [
                {'column-1': 'mtl'},
                {'column-1': 'sf'},
                {'column-1': 'mtl'},
                {'column-1': 'boston'}
            ],
            editable: true,
            id: 'table'
        }
    },

    {
        name: 'dropdown with column widths',
        props: {
            fill_width: false,
            style_data_conditional: [
                {if: {column_id: 'column-2'}, width: 400},
                {if: {column_id: 'column-3'}, width: 80}
            ],
            columns: [
                {
                    name: 'Column 1',
                    id: 'column-1',
                    type: ColumnType.Text,
                    presentation: Presentation.Dropdown
                },
                {
                    name: 'Column 2',
                    id: 'column-2',
                    type: ColumnType.Text,
                    presentation: Presentation.Dropdown
                },
                {
                    name: 'Column 3',
                    id: 'column-3',
                    type: ColumnType.Text,
                    presentation: Presentation.Dropdown
                }
            ],
            dropdown: {
                'column-1': {
                    options: [
                        {label: 'Montréal', value: 'mtl'},
                        {label: 'San Francisco', value: 'sf'}
                    ]
                },
                'column-2': {
                    options: [
                        {label: 'Montréal', value: 'mtl'},
                        {label: 'San Francisco', value: 'sf'}
                    ]
                },
                'column-3': {
                    options: [
                        {label: 'Montréal', value: 'mtl'},
                        {label: 'San Francisco', value: 'sf'}
                    ]
                }
            },
            data: [
                {'column-1': 'mtl', 'column-2': 'mtl', 'column-3': 'mtl'},
                {'column-1': 'mtl', 'column-2': 'mtl', 'column-3': 'mtl'},
                {'column-1': 'mtl', 'column-2': 'mtl', 'column-3': 'mtl'}
            ],
            editable: true,
            id: 'table'
        }
    },

    {
        name: 'multi-line headers',
        props: {
            columns: [
                {
                    name: ['Climate', 'Rainfall'],
                    id: 'rainfall'
                },
                {
                    name: ['Climate', 'Temperature'],
                    id: 'temp'
                },
                {
                    name: ['Climate', 'Rainfall'],
                    id: 'rainfall'
                },
                {
                    name: ['Water Conditions', 'Clarity'],
                    id: 'clarity'
                },
                {
                    name: ['Water Conditions', 'Salinity'],
                    id: 'salinity'
                },
                {
                    name: ['Region', ''],
                    id: 'region',
                    type: ColumnType.Text,
                    presentation: Presentation.Dropdown
                }
            ],
            dropdown: {
                region: {
                    options: [
                        {label: 'Hawaii', value: 'hawaii'},
                        {label: 'Costa Rica', value: 'costa-rica'}
                    ]
                }
            },
            merge_duplicate_headers: true,
            data: [
                {
                    rainfall: 1,
                    temp: 2,
                    rainfaill: 3,
                    clarity: 4,
                    salinity: 5,
                    region: 'hawaii'
                },
                {
                    rainfall: 10,
                    temp: 20,
                    rainfaill: 30,
                    clarity: 40,
                    salinity: 50,
                    region: 'costa-rica'
                }
            ],
            editable: true,
            id: 'table'
        }
    },

    {
        name: 'mixed percentage and pixel column widths',
        props: {
            id: 'table',
            fill_width: false,
            style_data_conditional: [
                {if: {column_id: 'column-2'}, width: 400},
                {if: {column_id: 'column-3'}, width: '30%'}
            ],
            columns: [
                {
                    name: 'Column 1',
                    id: 'column-1'
                },
                {
                    name: 'Column 2',
                    id: 'column-2'
                },
                {
                    name: 'Column 3',
                    id: 'column-3'
                }
            ],
            data: [
                {'column-1': 1, 'column-2': 2, 'column-3': 3},
                {'column-1': 10, 'column-2': 20, 'column-3': 30}
            ]
        }
    },

    {
        name: 'selection-borders-active-SW',
        props: {
            id: 'table',
            editable: true,
            selected_cells: [
                [1, 1],
                [1, 0],
                [0, 1],
                [0, 0]
            ],
            columns: [
                {
                    name: 'Column 1',
                    id: 'column-1'
                },
                {
                    name: 'Column 2',
                    id: 'column-2'
                }
            ],
            data: [
                {'column-1': 1, 'column-2': 'alpha'},
                {'column-1': 2, 'column-2': 'bravo'}
            ],
            active_cell: [1, 0]
        }
    },
    {
        name: 'selection-borders-active-NE',
        props: {
            id: 'table',
            editable: true,
            selected_cells: [
                [1, 1],
                [1, 0],
                [0, 1],
                [0, 0]
            ],
            columns: [
                {
                    name: 'Column 1',
                    id: 'column-1'
                },
                {
                    name: 'Column 2',
                    id: 'column-2'
                }
            ],
            data: [
                {'column-1': 1, 'column-2': 'alpha'},
                {'column-1': 2, 'column-2': 'bravo'}
            ],
            active_cell: [0, 1]
        }
    },

    {
        name: 'inner-selection',
        props: {
            id: 'table',
            editable: true,
            active_cell: [2, 1],
            selected_cells: [
                [2, 1],
                [2, 2],
                [1, 1],
                [1, 2]
            ],
            columns: [
                {
                    name: 'Column 1',
                    id: 'column-1'
                },
                {
                    name: 'Column 2',
                    id: 'column-2'
                },
                {
                    name: 'Column 3',
                    id: 'column-3'
                },
                {
                    name: 'Column 4',
                    id: 'column-4'
                }
            ],
            data: [
                {
                    'column-1': 1,
                    'column-2': 'alpha',
                    'column-3': 2,
                    'column-4': 1
                },
                {
                    'column-1': 2,
                    'column-2': 'bravo',
                    'column-3': 2,
                    'column-4': 1
                },
                {
                    'column-1': 3,
                    'column-2': 'charlie',
                    'column-3': 2,
                    'column-4': 1
                },
                {
                    'column-1': 4,
                    'column-2': 'delta',
                    'column-3': 2,
                    'column-4': 1
                }
            ]
        }
    },

    {
        name: 'per-cell dropdowns',
        props: {
            id: 'table',
            style_data_conditional: [{if: {column_id: 'column-1'}, width: 200}],
            columns: [
                {
                    id: 'column-1',
                    name: 'Column 1',
                    type: ColumnType.Text,
                    presentation: Presentation.Dropdown
                },
                {
                    id: 'column-2',
                    name: 'Column 2'
                }
            ],
            data: [
                {
                    'column-1': 'alpha',
                    'column-2': 1
                },
                {
                    'column-1': 'blue',
                    'column-2':
                        'Some really super long text that should overflow'
                },
                {
                    'column-1': 'apples',
                    'column-2': 1
                }
            ]
        }
    },

    {
        name: 'sortable, deletable, renamable columns',
        props: {
            id: 'table',
            columns: [
                {
                    name: ['City', 'NYC'],
                    id: 'city-nyc',
                    deletable: true,
                    renamable: true
                },
                {
                    name: ['City', 'SF'],
                    id: 'city-sf',
                    deletable: true
                },
                {
                    name: ['Weather', 'Rainy'],
                    id: 'weather-rainy',
                    renamable: true
                },
                {
                    name: ['Weather', 'Sunny'],
                    id: 'weather-sunny'
                },
                {
                    name: ['Village', 'NYC'],
                    id: 'village-nyc',
                    deletable: true,
                    renamable: [true, false]
                },
                {
                    name: ['Village', 'SF'],
                    id: 'village-sf',
                    deletable: true
                },
                {
                    name: ['Climate', 'Rainy'],
                    id: 'climate-rainy',
                    renamable: [false, true]
                },
                {
                    name: ['Climate', 'Sunny'],
                    id: 'climate-sunny'
                }
            ],
            data: [
                {
                    'city-nyc': 3,
                    'city-sf': 10,
                    'village-nyc': 3,
                    'village-sf': 10,
                    'weather-rainy': 15,
                    'weather-sunny': 20,
                    'climate-rainy': 15,
                    'climate-sunny': 20
                }
            ],
            merge_duplicate_headers: true,
            sortable: true,
            sort: []
        }
    }
];
