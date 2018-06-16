SAMPLE_TABLE_PROPS = [
    {
        'name': 'minimal',
        'props': {}
    },

    {
        'name': 'minimal-data',
        'props': {
            'dataframe': [{
                'x': 1
            }]
        }
    },

    {
        'name': 'minimal-columns',
        'props': {
            'columns': [{
                'name': 'column 1',
                'id': 'column-1'
            }]
        }
    },

    {
        'name': 'simple-columns-and-data',
        'props': {
            'columns': [
                {
                    'name': 'Column 1',
                    'id': 'column-1'
                },
                {
                    'name': 'Column 2',
                    'id': 'column-2'
                },
            ],
            'dataframe': [
                {'column-1': 1, 'column-2': 4},
                {'column-1': 2, 'column-2': 4},
            ]
        }
    },

    {
        'name': 'extra-columns',
        'props': {
            'columns': [
                {
                    'name': 'Column 1',
                    'id': 'column-1'
                },
                {
                    'name': 'Column 2',
                    'id': 'column-2'
                },
                {
                    'name': 'Column 3',
                    'id': 'column-3'
                }
            ],
            'dataframe': [
                {'column-1': 1, 'column-2': 2},
                {'column-1': 10, 'column-2': 20},
            ]
        }
    },

    {
        'name': 'extra-rows',
        'props': {
            'columns': [
                {
                    'name': 'Column 1',
                    'id': 'column-1'
                }
            ],
            'dataframe': [
                {'column-1': 3, 'column-2': 10},
                {'column-1': 30, 'column-2': 20}                
            ]
        }
    }

]
