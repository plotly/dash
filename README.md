## dash 2.0 - Deprecation Notice and Next Steps

April 20, 2016

tl;dr: We're no longer maintaining the code in this master branch. We're rethinking and rewriting `dash` to be an abstract web-application framework for technical computing. And we'd love your help. If you'd like to get involved, please reach out: chris@plot.ly (@chriddyp).

Here's some more context:

#### dash in 2014

`dash` started out with a really simple intent: provide some boiler plate code that shows python users how they can hook up their data analysis backends to some simple HTML controls like dropdowns to plotly.js graphs. The front-end is just jQuery, raw HTML controls, and the [skeleton CSS stylesheet](http://getskeleton.com). The back-end is just flask.

Writing data visualizations web-applications like this is actually a lot of work. You basically have to be a full-stack web-developer! It's inaccessible to the majority of scientists, statisticians, and analysts that might need to develop these data exploration applications in the first place.

#### Technical computing needs a better framework for creating user interfaces

There is a big gap in the technical computing and data science landscape when it comes to creating GUIs.

If you're a python user, you can assemble widgets like sliders and graphs together using the [Jupyter Notebook](http://moderndata.plot.ly/widgets-in-ipython-notebook-and-plotly/) interface or if you're a really savvy you could use [Matplotlib and Qt Designer](http://blog.rcnelson.com/building-a-matplotlib-gui-with-qt-designer-part-1/). These applications are both hard to distribute, inflexible aesthetically, and challenging to scale to advanced interfaces. In MATLAB you can create [GUIs with GUIDE](http://www.mathworks.com/videos/creating-a-gui-with-guide-68979.html) but you'll be faced with the same shortcomings in terms of design and distribution (not to mention license costs!). The Julia community hasn't yet adopted a solution (although [Escher.jl](https://shashi.github.io/Escher.jl/) looks promising and similar to the framework that we're proposing here). The best framework out there is R's Shiny. It's web based and is supported by an incredible community. Unfortunately, it's not supported in other languages. 

#### Web technologies in 2016 change everything

The development [react.js](https://facebook.github.io/react/) and [plotly.js](https://github.com/plotly/plotly.js) over the last couple of years have made it possible for all of this to change. We can now build a technical computing GUI framework using open web technologies.

- React.js makes it easier than ever to create and distribute the types of modular components that a GUI framework needs (sliders, dropdowns, tables, buttons). There are [over 2000 react components registered on NPM](https://www.npmjs.com/browse/keyword/react-component?offset=2000)!
- [plotly.js](https://github.com/plotly/plotly.js) provides an interface for creating super sophisticated scientific visualizations that were previously only available in packages like Matplotlib or MATLAB. plotly.js graphs are natively interactive in the web browser and over [20 chart types](https://plot.ly/javascript/) are supported including 3D graphs, high-performance webgl scatter plots, contour plots.
- CSS stylesheets and [inline CSS in React components](https://github.com/FormidableLabs/radium) provide a relatively portable way to customize these applications aesthetically.
- HTTP and JSON provide the interface between components to back-ends in different languages like Python, MATLAB, Julia, R.
- Simple server application frameworks like Flask in Python or Mux in Julia can connect the HTTP interface to the user's actual technical computing code.
- Services like heroku and AWS make these applications easy to deploy and share.

#### Introducing `dash (2.0)`

The `dash` project intends to be the software ecosystem to support a fully web-based technical computing GUI framework. The core of the project is a HTTP and JSON API that describes the layout and composition of components on a web page and how these components depend on each other. [Scroll down for an example of this API](#JSON-example) or [check out some prototypes](http://plotly-dash.herokuapp.com).

A web application written in `react.js`, `redux.js`, and an HTTP library like `xhr.js` will implement the front-end of these APIs. This application will render the components specified by the JSON spec. When a component's value changes (e.g. when a user drags a slider or clicks on a point in a graph), an HTTP request will be made with the component's updated value and the response of the request will update all of that component's dependents. A component registry will allow developers to plugin custom React components into their apps.

Like MATLAB's GUIDE, [plotly's dashboards.ly](https://dashboards.ly), and [Qt Designer](https://wiki.python.org/moin/PyQt/Creating_GUI_Applications_with_PyQt_and_Qt_Designer), the front-end will have an "edit" mode that will allow the developer to drag components around, resize them, or edit the components' state directly (e.g. change the text of a header or paragraph).

Separately, a Python framework will wrap the Flask server and provide a pythonic interface for describing the layout of app and responding to requests made from the front-end. Similar frameworks for MATLAB, Julia, and R will also be written on top of the JSON and HTTP spec.

#### Prototype

I've written a quick prototype of this stack in [this messy repo](https://github.com/chriddyp/messin) and you can check out [some examples and examine network requests online in these docs](https://plotly-dash.heroku.com) (itself built with dash!). The main ideas are there, but it needs to be re-written, tested, standardized, and less monolithic.

#### Community

If you'd like to get involved, please reach out! (chris@plot.ly). We're actively working on prototype and a beta release.

##### [Quick Example](#JSON-example)

Here's an example of what this might actually look like. [Check out full, working examples of a prototype in these docs](http://plotly-dash.herokuapp.com).


On page load, a JSON payload is served that describes the layout and composition of the components to be rendered in the web page:
```js
{
    "type": "div",  // all HTML elements are supported
    "props": {      // optional properties of this element like IDs, class names, styles. Custom components have additional custom properties.
        "style": {"color": "lightgrey"}
    },
    "children": [
        {
            "type": "Dropdown", // custom react dropdown component
            "props": {
                "id": "my-dropdown",
                "options": ["time", "voltage", "current"]
            }
        },
        {
            "type": "PlotlyGraph", // custom react component that renders a plotly graph
            "props": {
                "id": "my-graph",
                "dependencies": ["my-dropdown"], // when the component with the ID "my-dropdown" changes, an HTTP call with the dropdown's new value will be made to the server requesting new properties for this plotly graph
                "figure": {  // custom property that describes the graph
                    "data": [
                        {"x": [1, 2, 3], "y": [4, 1, 5], "type": "scatter"}
                    ]
                }
            }
        }
    ]
}
```

When the dropdown changes values, an HTTP call is made to the server with the new value of the dropdown:

```
POST /react
{
    "id": "my-dropdown",
    "value": "voltage"
}
```

And the server responds with the new values of the component's that "depend" on the dropdown. The developer of this app has complete control over the values in the response. This is where they can inject their technical computing code that might run models or query data. Their HTTP response will update components in the UI.
```
[
    {
        "id": "my-graph",
        "props": {
            "figure": {
                "data": [{"x": [3, 4, 5], "y": [5, 5, 42]}]
            }
        }
    }
]
```

The Python framework will abstract away the HTTP and the JSON. Writing an app like this might look like:

```python
import dash
from dash.components import div, Dropdown, PlotlyGraph
import plotly.graph_objs as go

# define the layout of the graph
dash.layout = div([
    Dropdown(options=['time', 'voltage', 'current'], id='my-dropdown'),
    PlotlyGraph(
        figure=go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 5])]),
        id='my-graph'
    )
], style=dict(color='lightgrey'))

# define how components get updated
@dash.react('my-graph', ['my-dropdown'])
def update_graph(dropdown_updates):
    selected_value = dropdown_updates.value

    # run some data analysis code using selected_value

    return go.Figure(data=Scatter(x=[3, 4, 5], y=[5, 5, 42]))
```

[Check out full, working examples of a prototype in these docs](http://plotly-dash.herokuapp.com)


#### Final Notes

Our technical computing community needs this. All too often our interface for running models is the terminal and the interface to view our results is a PDF. With a web-based GUI framework, we can use sliders to change the parameters of our models, click on points in a graph to drill down into data, run and record experiments with web-forms and buttons. We can make these interfaces gorgeous. We can share them in our communities through the web browser.

- @chriddyp (chris@plot.ly)

***

### Currently in this repo

Dash is an assemblage of Flask, Socketio, Jinja, Plotly and boiler plate CSS and JS for easily creating data visualization web-apps with your Python data analysis backend.

Getting Started
Check out the four examples:
- `$ python example-1-hello-world.py`
- `$ python example-2-etch-a-sketch.py`
- `$ python example-3-click-events.py`
![Hans Rosling Bubble Chart Style Interactive Web App](http://i.imgur.com/d3y4nwm.gif)

- `$ python example-4-tickers.py`
