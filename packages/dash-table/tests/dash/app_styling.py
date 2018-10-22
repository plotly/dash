from collections import OrderedDict
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from textwrap import dedent

import dash_table
from index import app
from .utils import html_table, section_title


def layout():
    data = OrderedDict(
        [
            ("Date", ["2015-01-01", "2015-10-24", "2016-05-10"] * 2),
            ("Region", ["Montreal", "Vermont", "New York City"] * 2),
            ("Temperature", [1, -20, 3.512] * 2),
            ("Humidity", [10, 20, 30] * 2),
            ("Pressure", [2, 10924, 3912] * 2),
        ]
    )

    df = pd.DataFrame(data)

    return html.Div(
        style={"marginLeft": "auto", "marginRight": "auto", "width": "80%"},
        children=[
            html.H1("[WIP] - Styling the Table"),

            section_title("HTML Table - Gridded"),

            html.Div("""
            By default, the Dash table has grey headers and borders
            around each cell. It resembles a spreadsheet with clearly defined
            headers
            """),

            html_table(
                df,
                cell_style={'border': 'thin lightgrey solid'},
                table_style={'width': '100%'},
                column_style={'width': '20%', 'paddingLeft': 20},
                header_style={'backgroundColor': 'rgb(235, 235, 235)'}
            ),

            html.Hr(),

            section_title("HTML Table - Column Alignment and Column Fonts"),
            dcc.Markdown(dedent(
            """
            When displaying numerical data, it's a good practice to use
            monospaced fonts, to right-align the data, and to provide the same
            number of decimals throughout the column.

            Note that it's not possible to modify the number of decimal places
            in css. `dash-table` will provide formatting options in the future,
            until then you'll have to modify your data before displaying it.

            For textual data, left-aligning the data is usually easier to read.

            In both cases, the column headers should have the same alignment
            as the cell content.
            """
            )),
            html_table(
                df,
                table_style={'width': '100%'},
                column_style={'width': '20%', 'paddingLeft': 20},
                cell_style={"paddingLeft": 5, "paddingRight": 5, 'border': 'thin lightgrey solid'},
                header_style_by_column={
                    "Temperature": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Humidity": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Pressure": {"textAlign": "right", "fontFamily": "monospaced"},
                },
                cell_style_by_column={
                    "Temperature": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Humidity": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Pressure": {"textAlign": "right", "fontFamily": "monospaced"},
                },
                header_style={'backgroundColor': 'rgb(235, 235, 235)'}
            ),

            html.Hr(),

            section_title('HTML Table - Styling the Table as a List'),

            dcc.Markdown(dedent('''
            The gridded view is a good default view for an editable table, like a spreadsheet.
            If your table isn't editable, then in many cases it can look cleaner without the
            horizontal or vertical grid lines.
            ''')),

            html_table(
                df,
                table_style={'width': '100%'},
                column_style={'width': '20%', 'paddingLeft': 20},
                cell_style={"paddingLeft": 5, "paddingRight": 5},
                header_style={'backgroundColor': 'rgb(235, 235, 235)', 'borderTop': 'thin lightgrey solid', 'borderBottom': 'thin lightgrey solid'},
                header_style_by_column={
                    "Temperature": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Humidity": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Pressure": {"textAlign": "right", "fontFamily": "monospaced"},
                },
                cell_style_by_column={
                    "Temperature": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Humidity": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Pressure": {"textAlign": "right", "fontFamily": "monospaced"},
                },
            ),

            html.Hr(),

            section_title('HTML Table - Row Padding'),

            dcc.Markdown(dedent('''
            By default, the gridded view is pretty tight. You can add some top and bottom row padding to
            the rows to give your data a little bit more room to breathe.
            ''')),

            html_table(
                df,
                table_style={'width': '100%'},
                column_style={'width': '20%', 'paddingLeft': 20},
                cell_style={"paddingLeft": 5, "paddingRight": 5},
                header_style={'backgroundColor': 'rgb(235, 235, 235)', 'borderTop': 'thin lightgrey solid', 'borderBottom': 'thin lightgrey solid'},
                header_style_by_column={
                    "Temperature": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Humidity": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Pressure": {"textAlign": "right", "fontFamily": "monospaced"},
                },
                cell_style_by_column={
                    "Temperature": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Humidity": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Pressure": {"textAlign": "right", "fontFamily": "monospaced"},
                },
                row_style={'paddingTop': 10, 'paddingBottom': 10}
            ),

            html.Hr(),

            section_title('HTML Table - List Style with Minimal Headers'),

            dcc.Markdown(dedent('''
            In some contexts, the grey background can look a little heavy.
            You can lighten this up by giving it a white background and
            a thicker bottom border.
            ''')),

            html_table(
                df,
                table_style={'width': '100%'},
                column_style={'width': '20%', 'paddingLeft': 20},
                cell_style={"paddingLeft": 5, "paddingRight": 5},
                header_style={'borderBottom': '2px lightgrey solid'},
                header_style_by_column={
                    "Temperature": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Humidity": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Pressure": {"textAlign": "right", "fontFamily": "monospaced"},
                },
                cell_style_by_column={
                    "Temperature": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Humidity": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Pressure": {"textAlign": "right", "fontFamily": "monospaced"},
                },
                row_style={'paddingTop': 10, 'paddingBottom': 10}
            ),

            html.Hr(),

            section_title('HTML Table - List Style with Understated Headers'),

            dcc.Markdown(dedent('''
            When the data is obvious, sometimes you can de-emphasize the headers
            as well, by giving them a lighter color than the cell text.
            ''')),

            html_table(
                df,
                table_style={'width': '100%'},
                column_style={'width': '20%', 'paddingLeft': 20},
                cell_style={"paddingLeft": 5, "paddingRight": 5},
                header_style={'color': 'rgb(100, 100, 100)'},
                header_style_by_column={
                    "Temperature": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Humidity": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Pressure": {"textAlign": "right", "fontFamily": "monospaced"},
                },
                cell_style_by_column={
                    "Temperature": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Humidity": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Pressure": {"textAlign": "right", "fontFamily": "monospaced"},
                },
                row_style={'paddingTop': 10, 'paddingBottom': 10}
            ),

            html.Hr(),

            section_title('HTML Table - Striped Rows'),

            dcc.Markdown(dedent('''
            When you're viewing datasets where you need to compare values within individual rows, it
            can sometimes be helpful to give the rows alternating background colors.
            We recommend using colors that are faded so as to not attract too much attention to the stripes.
            ''')),

            html_table(
                df,
                table_style={'width': '100%'},
                column_style={'width': '20%', 'paddingLeft': 20},
                cell_style={"paddingLeft": 5, "paddingRight": 5},
                header_style={'backgroundColor': 'rgb(235, 235, 235)', 'borderTop': 'thin lightgrey solid', 'borderBottom': 'thin lightgrey solid'},
                header_style_by_column={
                    "Temperature": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Humidity": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Pressure": {"textAlign": "right", "fontFamily": "monospaced"},
                },
                cell_style_by_column={
                    "Temperature": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Humidity": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Pressure": {"textAlign": "right", "fontFamily": "monospaced"},
                },
                row_style={'paddingTop': 10, 'paddingBottom': 10},
                odd_row_style={'backgroundColor': 'rgb(248, 248, 248)'}
            ),

            section_title('HTML Table - Dark Theme with Cells'),

            dcc.Markdown(dedent(
            """
            You have full control over all of the elements in the table.
            If you are viewing your table in an app with a dark background,
            you can provide inverted background and font colors.
            """
            )),

            html_table(
                df,
                table_style={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white',
                    'width': '100%'
                },
                cell_style={'border': 'thin white solid'},
                header_style={'backgroundColor': 'rgb(30, 30, 30)'},
                row_style={'padding': 10},
                header_style_by_column={
                    "Temperature": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Humidity": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Pressure": {"textAlign": "right", "fontFamily": "monospaced"},
                },
                cell_style_by_column={
                    "Temperature": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Humidity": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Pressure": {"textAlign": "right", "fontFamily": "monospaced"},
                },
            ),

            section_title('HTML Table - Dark Theme with Rows'),

            html_table(
                df,
                table_style={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white',
                    'width': '100%'
                },
                row_style={
                    'borderTop': 'thin white solid',
                    'borderBottom': 'thin white solid',
                    'padding': 10
                },
                header_style={'backgroundColor': 'rgb(30, 30, 30)'},
                header_style_by_column={
                    "Temperature": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Humidity": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Pressure": {"textAlign": "right", "fontFamily": "monospaced"},
                },
                cell_style_by_column={
                    "Temperature": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Humidity": {"textAlign": "right", "fontFamily": "monospaced"},
                    "Pressure": {"textAlign": "right", "fontFamily": "monospaced"},
                },
            ),

            section_title('HTML Table - Highlighting Certain Rows'),

            dcc.Markdown(dedent('''
            You can draw attention to certain rows by providing a unique
            background color, bold text, or colored text.
            ''')),

            html_table(
                df,
                cell_style={'border': 'thin lightgrey solid', 'color': 'rgb(60, 60, 60)'},
                table_style={'width': '100%'},
                column_style={'width': '20%', 'paddingLeft': 20},
                header_style={'backgroundColor': 'rgb(235, 235, 235)'},
                row_style_by_index={
                    4: {
                        'backgroundColor': 'yellow',
                    }
                }
            ),

            section_title('HTML Table - Highlighting Certain Columns'),

            dcc.Markdown(dedent('''
            Similarly, certain columns can be highlighted.
            ''')),

            html_table(
                df,
                cell_style={'border': 'thin lightgrey solid', 'color': 'rgb(60, 60, 60)'},
                table_style={'width': '100%'},
                column_style={'width': '20%', 'paddingLeft': 20},
                header_style={'backgroundColor': 'rgb(235, 235, 235)'},
                cell_style_by_column={
                    "Temperature": {
                        "backgroundColor": "yellow"
                    },
                }
            ),

            section_title('HTML Table - Highlighting Certain Cells'),

            dcc.Markdown(dedent('''
            You can also highlight certain cells. For example, you may want to
            highlight certain cells that exceed a threshold or that match
            a filter elsewhere in the app.
            ''')),

            html_table(
                df,
                cell_style={'border': 'thin lightgrey solid', 'color': 'rgb(60, 60, 60)'},
                table_style={'width': '100%'},
                column_style={'width': '20%', 'paddingLeft': 20},
                header_style={'backgroundColor': 'rgb(235, 235, 235)'},
                conditional_cell_style=lambda cell, column: (
                    {'backgroundColor': 'yellow'}
                    if (
                        (column == 'Region' and cell == 'Montreal')
                        or
                        (cell == 20)
                    ) else {}
                )
            ),

            html.Hr(),

            section_title('Dash Table - Styling the Table as a List'),
            # ...

            section_title('Dash Table - Row Padding'),
            dash_table.Table(
                id="styling-2",
                dataframe=df.to_dict("rows"),
                columns=[
                    {"name": i, "id": i} for i in df.columns
                ],
                style_data_conditional=[{ "padding_bottom": 5, "padding_top": 5}]
            ),

            section_title('Dash Table - List Style with Minimal Headers'),
            # ...

            section_title('Dash Table - List Style with Understated Headers'),
            # ...

            section_title('Dash Table - Striped Rows'),
            # ...

            section_title('Dash Table - Dark Theme with Cells'),
            dash_table.Table(
                id="styling-6",
                dataframe=df.to_dict("rows"),
                columns=[
                    {"name": i, "id": i} for i in df.columns
                ],
                content_style="grow",
                style_table={
                    "width": "100%"
                },
                style_data_conditional=[{
                    "background_color": "rgb(50, 50, 50)",
                    "color": "white",
                    "font_family": "arial"
                }, {
                    "if": { "column_id": "Humidity" },
                    "font_family": "monospace",
                    "padding_left": 20,
                    "text_align": "left"
                }, {
                    "if": { "column_id": "Pressure" },
                    "font_family": "monospace",
                    "padding_left": 20,
                    "text_align": "left"
                }, {
                    "if": { "column_id": "Temperature" },
                    "font_family": "monospace",
                    "padding_left": 20,
                    "text_align": "left"
                }]
            ),

            section_title('Dash Table - Dark Theme with Rows'),
            # ...

            section_title('Dash Table - Highlighting Certain Rows'),
            # ...

            section_title('Dash Table - Highlighting Certain Columns'),
            dash_table.Table(
                id="styling-9",
                dataframe=df.to_dict("rows"),
                columns=[
                    {"name": i, "id": i} for i in df.columns
                ],
                content_style="grow",
                style_table={
                    "width": "100%"
                },
                style_data_conditional=[{
                    "color": "rgb(60, 60, 60)",
                    "padding_left": 20,
                    "text-align": "left",
                    "width": "20%"
                }, {
                    "if": { "column_id": "Temperature" },
                    "background_color": "yellow"
                }]
            ),

            section_title('Dash Table - Highlighting Certain Cells'),
            dash_table.Table(
                id="styling-10",
                dataframe=df.to_dict("rows"),
                columns=[
                    {"name": i, "id": i} for i in df.columns
                ],
                content_style="grow",
                style_table={
                    "width": "100%"
                },
                style_data_conditional=[{
                    "if": { "column_id": "Region", "filter": "Region eq str(Montreal)" },
                    "background_color": "yellow"
                }, {
                    "if": { "column_id": "Humidity", "filter": "Humidity eq num(20)" },
                    "background_color": "yellow"
                }]
            )
        ],
    )
