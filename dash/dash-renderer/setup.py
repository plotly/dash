import json
from setuptools import setup
import dash
# import dash_core_components as dcc
from dash import dcc
# import dash_html_components as html
from dash import html
from dash.dependencies import Input, Output
import json

import pandas as pd
import plotly.express as px
from dash import dash_table
import numpy as np
import datetime
import plotly.graph_objects as pf

with open("package.json") as fp:
    package = json.load(fp)

setup(
    name="dash_renderer",
    version=package["version"],
    author="Chris Parmer",
    author_email="chris@plotly.com",
    packages=["dash_renderer"],
    include_package_data=True,
    license="MIT",
    description="Front-end component renderer for Dash",
    install_requires=[],
)




app = dash.Dash(__name__)



############################## MILESTONE 1 AND 2 #############################


# #  html layout
# app.layout = html.Div([
#     html.Div(id='input', children='hello world'),

#     html.Div(id='output'),

#     html.Div(id='output-2')
# ])


# # callback function 1
# @app.callback(Output('output', 'children'), Input('input', 'children'))
# def update_1(value):
#     pass

# # callback function 2
# @app.callback(Output('output-2', 'children'), Input('input', 'children'))
# def update_2(value):
#     serialized_object = {
#         '__type': 'JSON',
#         '__value': value
#     }
#     serialized_object = json.dumps(serialized_object)
#     return f'Output 2: {serialized_object}'




############################## MILESTONE 3 #############################

## serializer class
# class serializer:
#     def serialize(obj):
#         if str(type(obj)) == "<class 'pandas.core.frame.DataFrame'>":
#             return [{
#                 '__type': 'DataFrame',
#                 '__value': obj.to_dict('r')
#             }]

#     def deserializer(obj):
#         if obj[0]['__type'] == 'DataFrame':
#             return dict(pd.DataFrame(obj[0]['__value']))


## dataframe instance
# df = px.data.iris()

## html layout
# app.layout = html.Div([
#     dash_table.DataTable(data=serializer.serialize(df), id='input'),
#     html.Div(id='output')
# ])

## callback function
# @app.callback(Output('output', 'children'), Input('input', 'data'))
# def update(df_obj):
#     df = serializer.deserializer(df_obj)
#     return str(df)


############################## MILESTONE 4 #############################

# # dataframe instance
# df = px.data.iris()

# # html layout
# app.layout = html.Div([
#     dash_table.DataTable(data=[dict(df)], id='input'),
#     html.Div(id='output')
# ])


# # callback function
# @app.callback(Output('output', 'children'), Input('input', 'data'))
# def update(df):
#     return str(dict(pd.DataFrame(df)))


############################## MILESTONE 5 #############################


# # serializer class
# class serializer:
#     def serialize(obj):
#         list_obj = ["<class 'datetime.datetime'>"]
#         if  str(type(obj)) != list_obj:
#             return [{
#                 '__type': str(type(obj)),
#                 '__value': list(obj)
#             }]
#         else:
#             return [{
#                 '__type': str(type(obj)),
#                 '__value': [obj]
#             }]

#     def deserializer(obj):
#         # if obj[0]['__type'] == 'DataFrame':
#         return dict(pd.DataFrame(obj[0]['__value']))


# # dataframe instance
# # df = px.data.iris()
# # df = np.array([1,2,3,4])
# # df = datetime.datetime.now()
# df = pf.Figure(
#                 data=[pf.Bar(x=[1, 2, 3], y=[1, 3, 2])],
#                 layout=pf.Layout(title=pf.layout.Title(text="A Figure Specified By A Graph Object")
#     )
# )


# # html layout
# app.layout = html.Div([
#     dash_table.DataTable(data=serializer.serialize(df), id='input'),
#     html.Div(id='output')
# ])

# # callback function
# @app.callback(Output('output', 'children'), Input('input', 'data'))
# def update(df_obj):
#     df = serializer.deserializer(df_obj)
#     return str(df)




############################## MILESTONE 6 #############################

# serializer class
class serializer:
    def serialize(obj):
        if  str(type(obj)) != "<class 'datetime.datetime'>":
            return [{
                # '__type': str(type(obj)),
                '__value': list(obj)
            }]
        else:
            return [{
                # '__type': str(type(obj)),
                '__value': [obj]
            }]

    def deserializer(obj):
        # if obj[0]['__type'] == 'DataFrame':
        return dict(pd.DataFrame(obj[0]['__value']))


# dataframe instance
df = px.data.iris()
# df = np.array([1,2,3,4])
# df = datetime.datetime.now()
# df = pf.Figure(
#                 data=[pf.Bar(x=[1, 2, 3], y=[1, 3, 2])],
#                 layout=pf.Layout(title=pf.layout.Title(text="A Figure Specified By A Graph Object")
#     )
# )


# html layout
app.layout = html.Div([
    dash_table.DataTable(data=serializer.serialize(df), id='input'),
    html.Div(id='output')
])

# callback function
@app.callback(Output('output', 'children'), Input('input', 'data'))
def update(df_obj):
    df = serializer.deserializer(df_obj)
    return str(df)




# run the server
if __name__ == '__main__':
    app.run_server(debug=True)
