from copy import deepcopy
from dash import Dash
from dash_core_components import Dropdown, PlotlyGraph
from dash_html_components import B, Div, Pre, H1, P
import json
import plotly.plotly as py

# Download the contour plot from https://plot.ly
py.sign_in("PlotBot", "da05144j7i")
fig = py.get_figure("https://plot.ly/~chris/5496")
margin = {'l': 20, 'r': 20, 'b': 20, 't': 20}
fig['layout'].update({'margin': margin})

figmain = deepcopy(fig)
figmain['layout'].update({'width': 500, 'height': 500})
figmain['data'][0]['showscale'] = False

figx = {'data': [], 'layout': {'width': 200, 'height': 500}}
figy = {'data': [], 'layout': {'width': 500, 'height': 200}}


dash = Dash(__name__)
dash.layout = Div([
    H1('click events'),
    P('click on a heatmap cell to view an x, y slice through your cursor'),
    Div([
        PlotlyGraph(
            id='yslice',
            width=figy['layout']['width'],
            height=figy['layout']['height'],
            data=figy['data'],
            layout=figy['layout']),
        Div([
            PlotlyGraph(
                id='heatmap',
                bindClick=True,
                width=figmain['layout']['width'],
                height=figmain['layout']['height'],
                data=figmain['data'],
                layout=figmain['layout']),
        ]), # style={"display": "inline-block"}
        Div([
            PlotlyGraph(
                id='xslice',
                width=figx['layout']['width'],
                height=figx['layout']['height'],
                layout=figx['layout'],
                data=figx['data']),
        ]) # style={"display": "inline-block"}
    ], className="row"),

    Div([
        B('click callback'),
        Pre(id="event-info") # style={"overflowY": "scroll"}
    ])
])


def display_graph_event_info(heatmap):
    """Display the click object in the <pre id="event-info">.
    This function gets called when the user hovers over or clicks on
    points in the heatmap. To assign click events to graphs, set
    bindClick=True in the PlotlyGraph component.
    """
    clickData = ''
    props = heatmap['props']
    if hasattr(props, 'clickData'):
        print('has clickData')
        clickData = json.dumps(heatmap.clickData, indent=4)
    else:
        print('no clickData')

    return {
        'content': repr(heatmap)+'\nclickData: '+clickData
    }

dash.react('event-info', ['heatmap'])(display_graph_event_info)

# def plot_yslice(heatmap_graph):
#     """ Update the "yslice" graph with the slice of data that the user has
#     clicked on.
#     This function gets called on click events fired from the
#     "heatmap" graph.
#     """
#     props = heatmap_graph['props']

#     if (hasattr(props, 'clickData')):
#         event_data = getattr(props, 'clickData')
#         point = event_data['points'][0]['pointNumber']
#         rowNumber = point[1]
#         trace = heatmap_graph.figure['data'][0]
#         row = trace['z'][rowNumber]
#         x = trace.get('y', range(len(trace['z'][0])))

#         return {
#             'data': [{
#                 'x': x,
#                 'y': row
#             }],
#             'layout': {
#                 'margin': margin
#             }
#         }

# dash.react('yslice', ['heatmap'])(plot_yslice)

def plot_xslice(heatmap_graph):
    """ Update the "xslice" graph with the slice of data that the user has
    clicked on.
    This function gets called on click events fired from the
    "heatmap" graph.
    """
    props = heatmap_graph['props']

    # Initialize data and layout props for return
    data = []
    layout = {}

    # Clone existing props, if possible
    if (hasattr(props, 'data')):
        data = getattr(props, 'data')

    if(hasattr(props, 'layout')):
        layout = getattr(props, 'layout')

    # See if we have click data from the event
    if (hasattr(props, 'clickData')):
        event_data = getattr(props, 'clickData')
        point = event_data['points'][0]['pointNumber']
        colNumber = point[0]
        trace = heatmap_graph.figure['data'][0]
        column = [zi[colNumber] for zi in trace['z']]
        y = trace.get('y', range(len(trace['z'])))

        data = [{
            'x': column,
            'y': y
        }]

        layout = {
            'margin': margin
        }

    # Return the resulting props
    return {
        'data': data,
        'layout': layout
     }

dash.react('xslice', ['heatmap'])(plot_xslice)


if __name__ == "__main__":
    dash.server.run(port=8050, debug=True)
