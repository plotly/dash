from collections import OrderedDict
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from textwrap import dedent

import dash_table
from index import app
from .utils import section_title


ID_PREFIX = "app_dropdown"
IDS = {
    "dropdown": ID_PREFIX,
    "dropdown-by-cell": '{}-row-by-cell'.format(ID_PREFIX)
}


df = pd.DataFrame(OrderedDict([
    ('climate',
     ['Sunny', 'Snowy', 'Sunny', 'Rainy']),
    ('temperature',
     [13, 43, 50, 30]),
    ('city',
     ['NYC', 'Montreal', 'Miami', 'NYC'])
]))

df_per_row_dropdown = pd.DataFrame(OrderedDict([
    ('City',
     ['NYC', 'Montreal', 'Los Angeles']),
    ('Neighborhood',
     ['Brooklyn', 'Mile End', 'Venice']),
    ('Temperature (F)',
     [70, 60, 90]),
]))


def layout():
    return html.Div([

        dcc.Markdown(dedent('''
        The Dash table includes support for per-column and
        per-cell dropdowns. In future releases, this will
        be tightly integrated with a more formal typing system.

        For now, use the dropdown renderer as a way to limit the
        options available when editing the values with an editable table.

        ''')),

        section_title('Dash Table with Per-Column Dropdowns'),

        dash_table.Table(
            id=IDS['dropdown'],
            data=df.to_dict('rows'),
            columns=[
                {'id': 'climate', 'name': 'climate'},
                {'id': 'temperature', 'name': 'temperature'},
                {'id': 'city', 'name': 'city'},
            ],

            editable=True,
            column_static_dropdown=[
                {
                    'id': 'climate',
                    'dropdown': [
                        {'label': i, 'value': i}
                        for i in df['climate'].unique()
                    ]
                },
                {
                    'id': 'city',
                    'dropdown': [
                        {'label': i, 'value': i}
                        for i in df['city'].unique()
                    ]
                },
            ]
        ),

        section_title('Dash Table with Per-Cell Dropdowns via Filtering UI'),

        dash_table.Table(
            id=IDS['dropdown-by-cell'],
            data=df_per_row_dropdown.to_dict('rows'),
            columns=[
                {'id': c, 'name': c}
                for c in df_per_row_dropdown.columns
            ],

            editable=True,
            column_conditional_dropdowns=[
                {
                    'id': 'Neighborhood',
                    'dropdowns': [

                        {
                            'condition': 'City eq "NYC"',
                            'dropdown': [
                                {'label': i, 'value': i}
                                for i in [
                                    'Brooklyn',
                                    'Queens',
                                    'Staten Island'
                                ]
                            ]
                        },

                        {
                            'condition': 'City eq "Montreal"',
                            'dropdown': [
                                {'label': i, 'value': i}
                                for i in [
                                    'Mile End',
                                    'Plateau',
                                    'Hochelaga'
                                ]
                            ]
                        },

                        {
                            'condition': 'City eq "Los Angeles"',
                            'dropdown': [
                                {'label': i, 'value': i}
                                for i in [
                                    'Venice',
                                    'Hollywood',
                                    'Los Feliz'
                                ]
                            ]
                        }

                    ]
                }
            ]
        ),

        section_title('Dash Table with Per-Cell Dropdowns'),

        html.Div('This example uses a deprecated API, `dropdown_properties`.'),

        dash_table.Table(
            id=IDS['dropdown-by-cell'],
            data=df_per_row_dropdown.to_dict('rows'),
            columns=[
                {'id': c, 'name': c}
                for c in df_per_row_dropdown.columns
            ],

            editable=True,
            dropdown_properties=[
                {
                    'options': [
                        {'label': i, 'value': i}
                        for i in [
                            'Brooklyn',
                            'Queens',
                            'Staten Island'
                        ]
                    ]
                },

                {
                    'options': [
                        {'label': i, 'value': i}
                        for i in [
                            'Mile End',
                            'Plateau',
                            'Hochelaga'
                        ]
                    ]
                },

                {
                    'options': [
                        {'label': i, 'value': i}
                        for i in [
                            'Venice',
                            'Hollywood',
                            'Los Feliz'
                        ]
                    ]
                },
            ]

        ),

    ])
