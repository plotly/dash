## Dash
Dash is an assemblage of Flask, Socketio, Jinja, and Plotly for easily creating
data visualization web-apps with a Python data analysis backend.

![](http://i.imgur.com/we68GEC.gif)

```python
from collections import deque

from Templatize import HTMLElement as H
from Templatize import WriteTemplate


class Dash():
    def __init__(self):
        self.graph_id = 'top_graph'
        self.slider_x = 'X'
        self.slider_y = 'Y'
        self.title_input = 'title'

        # Title
        WriteTemplate('banner', [H('h1', {}, 'Etch-a-sketch')])

        WriteTemplate('leftcolumn', [
            # First slider
            H('label', {'for': self.slider_x}, 'X Position'),
            H('input', {
                'type': 'range',
                'class': 'u-full-width show-values',
                'name': self.slider_x,
                'value': 0,
                'min': 10,
                'max': 2000,
                'step': 10
            }),

            # Second slider
            H('label', {'for': self.slider_y}, 'Y Position'),
            H('input', {
                'type': 'range',
                'class': 'u-full-width show-values',
                'name': self.slider_y,
                'value': 0,
                'min': 10,
                'max': 2000,
                'step': 10
            }),

            H('label', {}, 'Title'),
            H('input', {
                'class': 'u-full-width',
                'type': 'text',
                'placeholder': 'Type away',
                'name': self.title_input})
        ])

        WriteTemplate('rightcolumn', [
            H('iframe', dict(id=self.graph_id,
                             src="https://plot.ly/~playground/7.embed",
                             style="width: 100%; height: 500px; border: none;"))
        ])

        self.last_x = deque([], 100)
        self.last_y = deque([], 100)

    def on_page_load(self):
        pass

    def on_pong(self, message):
        messages = []
        return messages

    def replot(self, app_state):
        self.last_x.append(app_state[self.slider_x])
        self.last_y.append(app_state[self.slider_y])
        messages = [
            {
                'id': self.graph_id,
                'task': 'newPlot',
                'layout': {
                    'title': app_state[self.title_input]
                },
                'data': [{
                    'x': list(self.last_x),
                    'y': list(self.last_y)
                }]
            }
        ]

        return messages
```

### Usage
```
$ python app.py
```


### Credits
Dash is inspired by:
- R's Shiny
- IPython notebook's widgets
- Spyre

Check them out!
