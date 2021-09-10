from dash import Dash, Input, Output, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import dash_table as dt


# DROPDOWN EXAMPLE - bar-charts
def test_mssh001_bar_charts(dash_duo):
    app = Dash(__name__)

    df = px.data.tips()

    dropdown = dcc.Dropdown(df.day.unique(), value="Sun")
    barchart = dcc.Graph()
    app.layout = dbc.Container([dropdown, barchart])

    @app.callback(Output(barchart, "figure"), Input(dropdown, "value"))
    def update(day):
        return px.bar(
            df["day"] == day, x="sex", y="total_bill", color="smoker", barmode="group"
        )

    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []


# SLIDER EXAMPLE - line-and-scatter
def test_mssh002_line_and_scatter(dash_duo):
    app = Dash(__name__)

    df = px.data.iris()

    graph = dcc.Graph()
    label = dbc.Label("Petal Width:")
    slider = dcc.RangeSlider(0, 2.5)

    app.layout = dbc.Container([graph, label, slider])

    @app.callback(Output(graph, "figure"), Input(slider, "value"))
    def update(slider_range):
        low, high = slider_range
        mask = (df["petal_width"] > low) & (df["petal_width"] < high)
        return px.scatter(
            df[mask],
            x="sepal_width",
            y="sepal_length",
            color="species",
            size="petal_length",
            hover_data=["petal_width"],
        )

    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []


# CHECKLIST EXAMPLE - line-charts
def test_mssh003_checklist_example_line_charts(dash_duo):
    app = Dash(__name__)

    df = px.data.gapminder()
    continents = df.continent.unique()

    app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

    cl = dcc.Checklist(continents, value=continents[3:], inline=True)
    graph = dcc.Graph()
    app.layout = dbc.Container([cl, graph])

    @app.callback(Output(graph, "figure"), Input(cl, "value"))
    def update(continents):
        return px.line(
            df[df.continent.isin(continents)], x="year", y="lifeExp", color="country"
        )

    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []


# BUTTON EXAMPLE - axes
def test_mssh004_button_axes(dash_duo):
    app = Dash(__name__)

    df = px.data.tips()

    graph = dcc.Graph()
    btn = html.Button("Rotate", n_clicks=0)
    app.layout = dbc.Container([graph, btn])

    @app.callback(Output(graph, "figure"), Input(btn, "n_clicks"))
    def rotate_figure(n_clicks):
        return px.histogram(df, x="sex").update_xaxes(tickangle=n_clicks * 45)

    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []


# TABLE EXAMPLE
def test_mssh005_table_example(dash_duo):
    app = Dash(__name__)

    df = pd.read_csv("https://git.io/Juf1t")

    app.layout = dbc.Container(
        [
            dbc.Label("Click a cell in the table:", id="out"),
            dt.DataTable(df.to_dict("records"), id="tbl"),
        ]
    )

    @app.callback(Output("out", "children"), Input("tbl", "active_cell"))
    def update(active_cell):
        return str(active_cell)

    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []


# RADIO BUTTONS - legend
def test_mssh006_radio_buttons(dash_duo):
    app = Dash(__name__)

    # Define the figure
    df = px.data.gapminder().query("year==2007")

    graph = dcc.Graph()
    x = dcc.RadioItems({"left": 0, "right": 1}, id="x", inline=True)
    y = dcc.RadioItems({"top": 0, "bottom": 1}, id="y", inline=True)
    label = dbc.Label("Legend position")

    app.layout = dbc.Container([graph, label, x, y])

    @app.callback(Output(graph, "figure"), [Input(x, "value"), Input(y, "value")])
    def update(pos_x, pos_y):
        return px.scatter(
            df,
            x="gdpPercap",
            y="lifeExp",
            color="continent",
            size="pop",
            size_max=45,
            log_x=True,
        ).update_layout(legend_x=pos_x, legend_y=pos_y)

    dash_duo.start_server(app)
    assert dash_duo.get_logs() == []
