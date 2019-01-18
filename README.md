# Dash

#### Dash is a Python framework for building analytical web applications. No JavaScript required.

Build on top of Plotly.js, React, and Flask, Dash ties modern UI elements like dropdowns, sliders, and graphs directly to your analytical python code.

[![CircleCI](https://circleci.com/gh/plotly/dash.svg?style=svg)](https://circleci.com/gh/plotly/dash)

[ONLINE DOCUMENTATION](https://dash.plot.ly/getting-started)

[OFFLINE (PDF) DOCUMENTATION](https://github.com/plotly/dash-docs/blob/master/pdf-docs/Dash_User_Guide_and_Documentation.pdf)

[DASH DOCS ON HEROKU](http://dash-docs.herokuapp.com/) (for corporate networks that cannot access plot.ly)


Here’s a 43-line example of a Dash App that ties a Dropdown to a D3.js Plotly Graph.
As the user selects a value in the Dropdown, the application code dynamically
exports data from Google Finance into a Pandas DataFrame. This app was written in just 43 lines of code ([view the source](https://gist.github.com/chriddyp/3d2454905d8f01886d651f207e2419f0)).

![Sample Dash App](https://user-images.githubusercontent.com/1280389/30086128-9bb4a28e-9267-11e7-8fe4-bbac7d53f2b0.gif)

Dash app code is declarative and reactive, which makes it easy to build complex apps that contain many interactive elements. Here’s an example with 5 inputs, 3 outputs, and cross filtering. This app was composed in just 160 lines of code, all of which were Python.

![crossfiltering dash app](https://user-images.githubusercontent.com/1280389/30086123-97c58bde-9267-11e7-98a0-7f626de5199a.gif)

Dash uses [Plotly.js](https://github.com/plotly/plotly.js) for charting. Over 35 chart types are supported, including maps.

 ![Dash app with Mapbox map showing walmart store openings](https://user-images.githubusercontent.com/1280389/30086299-768509d0-9268-11e7-8e6b-626ac9ca512c.gif)
 
Dash isn't just for dashboards. You have full control over the look and feel of your applications. Here's a Dash app that's styled to look like a PDF report.

![goldman sachs report](https://user-images.githubusercontent.com/1280389/30086373-d076a372-9268-11e7-99df-d84fa69f3e20.gif)

To learn more about Dash, read the [extensive announcement letter](https://medium.com/@plotlygraphs/introducing-dash-5ecf7191b503) or [jump in with the user guide](https://plot.ly/dash).

### Documentation

View the [Dash User Guide](https://plot.ly/dash). It's chock-full of examples, pro tips, and guiding principles.

### Licensing

Dash is licensed under MIT.

For companies with software budgets, Plotly offers [Dash Deployment Server](https://plot.ly/dash/pricing/), an enterprise-ready platform for hosting Dash apps in a private cloud or on your own servers. [Learn more about Dash Deployment Server](https://plot.ly/dash/pricing/).

### Contact and Support

See [https://plot.ly/dash/support](https://plot.ly/dash/support) for ways to get in touch.

***

![image](https://user-images.githubusercontent.com/1280389/30084008-9fbc68fc-925e-11e7-891c-18a9b8f6ac6b.png)
