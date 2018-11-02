# Dash Table 3.1

An interactive `DataTable` for [Dash](https://dash.plot.ly/).

[View the docs to get started](https://dash.plot.ly/datatable)

```python
import dash
import dash_table
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

app = dash.Dash(__name__)

app.layout = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict("rows"),
)

if __name__ == '__main__':
    app.run_server(debug=True)
```

![Interactive Dash DataTable](https://user-images.githubusercontent.com/1280389/47935912-67187080-deb2-11e8-8936-34b0c99b518f.png)

***

The DataTable is an interactive table component designed for
viewing, editing, and exploring large datasets.

It's rendered with standard, semantic <table/> markup,
making it accessible, responsive, and easy to style.

This component was written from scratch in React.js
specifically for the Dash community.
Its API was designed to be ergonomic and its behavior is completely
customizable through its properties.

7 months in the making, this is the most complex component
that we've written in React! It's already feature-rich and
 we're excited to continue to invest in its future.

DataTable is in alpha. This is more of a statement on its API
rather than on its features. The table works really well right now,
we just expect to make a few more breaking changes to its API and
behavior within the next couple of months. Once the community
feels good about its API, we'll lock it down and we'll commit to
reducing the frequency of breaking changes.
Subscribe to [dash-table#207](https://github.com/plotly/dash-table/207)
to stay up-to-date with breaking changes.

So, use the table and let us know what you think.
Keep an eye on the [CHANGELOG.md](https://github.com/plotly/dash-table/blob/master/CHANGELOG.md)
to be aware of breaking changes,
upgrade guides, and new features.

***

**Contributing**

See [CONTRIBUTING.md](https://github.com/plotly/dash-table/blob/master/CONTRIBUTING.md)
