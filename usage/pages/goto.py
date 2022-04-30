#
"""
Example of:
  1) 2 variables embedded in a path
  2) Updating the URL in a callback rather than the user clicking a link.
  Note -- this layout is not updated in dash.page_container when dcc.Location(id="url", refresh=False)
  Set refresh=True, or manually refresh the page to update.  However, the "custom-output" div in app.py updates.



"""

import dash
from dash import html, Output, Input, callback, ctx
import random


dash.register_page(
    __name__,
    path_template="/goto-<data>-and-<data2>-data",
    path="/goto-br1-and-br2-data",
)


def layout(data=None, data2=None):
    return dash.html.Div(
        [html.Button("goto", id="goto", n_clicks=0), f"goto:  {data}-{data2}"],
    )


@callback(
    Output("url", "pathname"), Input("goto", "n_clicks"), prevent_initial_call=True
)
def goto(n):
    if n > 0:
        x = random.randrange(1, 10)
        return f"goto-{x}-and-{x+2}-data"
    return dash.no_update
