dash is a generic, web-based API for assembling modular components into dynamic web applications.

similar projects include:
- R's Shiny
- Jupyter Widgets
- Plotly's [dashboards.ly](https://dashboards.ly)

dash is composed of several parts:
- a JSON API that describes the layout and composition of the web applications
- an HTTP API that specifies how components depend on each other and how components should update when the front-end state changes
- a front-end implementation of these APIs written with React and redux ([`renderer`](https://github.com/plotly/dash2/tree/master/renderer))
- a back-end implementation of the HTTP API written with Python and Flask
- a web-based user interface for creating, editing, and re-arranging these layouts written in React

this repo contains prototypes of these components.
