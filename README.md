# Dash

[![CircleCI](https://img.shields.io/circleci/project/github/plotly/dash/master.svg)](https://circleci.com/gh/plotly/dash)
[![GitHub](https://img.shields.io/github/license/plotly/dash.svg?color=dark-green)](https://github.com/plotly/dash/blob/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/dash.svg?color=dark-green)](https://pypi.org/project/dash/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dash.svg?color=dark-green)](https://pypi.org/project/dash/)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/y/plotly/dash.svg?color=dark-green)](https://github.com/plotly/dash/graphs/contributors)
[![LGTM Alerts](https://img.shields.io/lgtm/alerts/g/plotly/dash.svg)](https://lgtm.com/projects/g/plotly/dash/alerts)
[![LGTM Grade](https://img.shields.io/lgtm/grade/python/g/plotly/dash.svg)](https://lgtm.com/projects/g/plotly/dash/context:python)


#### *Dash is a Python framework for building analytical web applications. No JavaScript required*.

Built on top of Plotly.js, React and Flask, Dash ties modern UI elements like dropdowns, sliders, and graphs directly to your analytical Python code. Read our tutorial proudly crafted ❤️ by Dash itself.

- [User Guide](https://dash.plot.ly/getting-started)

- [Offline (PDF) Documentation](https://github.com/plotly/dash-docs/blob/master/pdf-docs/Dash_User_Guide_and_Documentation.pdf)

- [Dash Docs on Heroku](http://dash-docs.herokuapp.com/) (for corporate network that cannot access plot.ly)


### Embed dash applications in react

It's possible to embed a dash app in a react app. We need a few tweaks

- Manually add dash dependencies: Dash Python server generates an index.html that loads all its depndencies.
(React, DashRenderer, Dash component suites). The  python backend app introspect the code and knows which components suite to load. For embedding dash in a react app,
we need to build ourselves the index.html
- Add the dash configuration. Dash backend insert a `<script>` tag with the dash configuration. We pass the config as a JSON object directly to the React components ( `AppProvider` `AppContainer`)
- Use the reset flag for initializing the redux store. We need a new store when we switch app
- Either proxy the calls to the correct dash backend, or mount the dash apps in a flask server on
different endpoints


### How to make this work

To make this example work, you'll need to have two dash apps running and served on the 
ports that are used in the proxy configuration.

Clicking on the switch button on the bottom of the screen will switch the dash applications

To start the app, from the project folder :

```cd dash-renderer```

`npm run start`
