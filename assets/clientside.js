window.clientside = {

    display: function (value) {
        return 'Client says "' + value + '"';
    },

    updateFig: function(search, years, mode, rows) {
        var filtered_rows = R.filter(
          R.allPass([
            R.compose(
              R.contains(search),
              R.prop('country')
            ),
            R.compose(
              R.flip(R.contains)(years),
              R.prop('year')
          ),
        ]), rows);

        return {
            'data': [{
                'x': R.pluck('gdpPercap', filtered_rows),
                'y': R.pluck('lifeExp', filtered_rows),
                'text': R.map(
                    R.join(' - '),
                    R.zip(
                        R.pluck('year', filtered_rows),
                        R.pluck('country', filtered_rows)
                    )
                ),
                'type': 'scatter',
                'mode': mode,
                'marker': {
                    'opacity': 0.7
                }
            }],
            'layout': {
                'hovermode': 'closest',
                'xaxis': {'type': 'log'}
            }
        }
    },

    mean: function(...args) {
        console.warn('mean.args: ', args);
        const meanValues = R.mean(args);
        console.warn('meanValues: ', meanValues);
        return meanValues;
    },

    tableColumns: function(
        addColumnNClicks, newColumnName, existingColumns
    ) {
        if (addColumnNClicks === 0) {
            return [{'id': 'column-1', 'name': 'Column 1'}];
        }
            return R.concat(
                existingColumns,
                [{
                    'name': newColumnName,
                    'id': Math.random().toString(36).substring(7)
                }]
            );

    },

    tableData: function(columns, n_clicks, data) {
        if (n_clicks === 0 && columns.length === 1) {
            return initial_data;
        } else if (R.isNil(data)) {
            return [{'column-1': 9}];
        } else if (columns.length > R.values(data[0]).length) {
            return data.map(row => {
                const newCell = {};
                newCell[columns[columns.length - 1].id] = 9;
                return R.merge(row, newCell)
            });
        } else if(n_clicks > data.length) {
            const newRow = {};
            columns.forEach(col => newRow[col.id] = 9);
            return R.concat(
                data,
                [newRow]
            );
        }
    },

    graphTable(data) {
        return {
            'data': [{
                'z': R.map(R.values, data),
                'type': 'heatmap'
            }]
        }
    },

    animateFig: function(countries, year, rows) {
        var filtered_rows = R.filter(
          R.allPass([
            R.compose(
                R.flip(R.contains)(countries),
                R.prop('country')
            ),
            R.propEq('year', year)
          ]), rows);

        return {
            'data': [{
                'x': R.pluck('gdpPercap', filtered_rows),
                'y': R.pluck('lifeExp', filtered_rows),
                'text': R.map(
                    R.join(' - '),
                    R.zip(
                        R.pluck('year', filtered_rows),
                        R.pluck('country', filtered_rows)
                    )
                ),
                'type': 'scatter',
                'mode': 'markers',
                'marker': {
                    'opacity': 0.7,
                    'size': 12
                }
            }],
            'layout': {
                'hovermode': 'closest',
                'xaxis': {
                    'type': 'log',
                    'range': [2, 5]
                },
                'yaxis': {
                    'range': [15, 90]
                }
            }
        }
    },


}
