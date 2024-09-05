# Dash Table

An interactive `DataTable` for [Dash](https://dash.plotly.com/).

:point_right: [Documentation](https://dash.plotly.com/datatable)

## Quickstart

```
pip install dash
```

```python
from dash import Dash, dash_table
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

app = Dash(__name__)

app.layout = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'),
)

if __name__ == '__main__':
    app.run_server(debug=True)
```

![Interactive Dash DataTable](https://user-images.githubusercontent.com/1280389/47935912-67187080-deb2-11e8-8936-34b0c99b518f.png)

## Background

Dash DataTable is an interactive table component designed for viewing, editing, and exploring large datasets.

DataTable is rendered with standard, semantic HTML `<table/>` markup, which makes it accessible, responsive, and easy to style.

This component was written from scratch in React.js and Typescript specifically for the Dash community. Its API was designed to be ergonomic and its behavior is completely customizable through its properties.

DataTable was designed with a featureset that allows that Dash users to create complex, spreadsheet driven applications with no compromises. We're excited to continue to work with users and companies that [invest in DataTable's future](https://plotly.com/products/consulting-and-oem/).

Note: DataTable is currently supported in Chrome, Firefox, Safari, Edge (version 15+), and Internet Explorer 11.

Share your DataTable Dash apps on the [community forum](https://community.plotly.com/t/show-and-tell-community-thread/7554)!

## Contributing

See [CONTRIBUTING.md](https://github.com/plotly/dash-table/blob/master/CONTRIBUTING.md)
