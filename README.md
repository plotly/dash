# Dash

[![CircleCI](https://img.shields.io/circleci/project/github/plotly/dash/master.svg)](https://circleci.com/gh/plotly/dash)
[![GitHub](https://img.shields.io/github/license/plotly/dash.svg?color=dark-green)](https://github.com/plotly/dash/blob/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/dash.svg?color=dark-green)](https://pypi.org/project/dash/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dash.svg?color=dark-green)](https://pypi.org/project/dash/)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/y/plotly/dash.svg?color=dark-green)](https://github.com/plotly/dash/graphs/contributors)

#### *Dash is the most downloaded, trusted Python framework for building ML & data science web apps*.

Built on top of [Plotly.js](https://github.com/plotly/plotly.js), [React](https://reactjs.org/) and [Flask](https://palletsprojects.com/p/flask/), Dash ties modern UI elements like dropdowns, sliders, and graphs directly to your analytical Python code. Read [our tutorial](https://dash.plotly.com/getting-started) (proudly crafted ❤️ with Dash itself).

- [Docs](https://dash.plotly.com/getting-started): Create your first Dash app in under 5 minutes

- [dash.gallery](https://dash.gallery): Dash app gallery with Python & R code

### Dash App Examples

| Dash App | Description |
|--- | :---: |
|![Sample Dash App](https://user-images.githubusercontent.com/1280389/30086128-9bb4a28e-9267-11e7-8fe4-bbac7d53f2b0.gif) | Here’s a simple example of a Dash App that ties a Dropdown to a Plotly Graph. As the user selects a value in the Dropdown, the application code dynamically exports data from Google Finance into a Pandas DataFrame. This app was written in just **43** lines of code ([view the source](https://gist.github.com/chriddyp/3d2454905d8f01886d651f207e2419f0)). |
|![Crossfiltering Dash App](https://user-images.githubusercontent.com/1280389/30086123-97c58bde-9267-11e7-98a0-7f626de5199a.gif)|Dash app code is declarative and reactive, which makes it easy to build complex apps that contain many interactive elements. Here’s an example with 5 inputs, 3 outputs, and cross filtering. This app was composed in just 160 lines of code, all of which were Python.|
|![Dash App with Mapbox map showing walmart store openings](https://user-images.githubusercontent.com/1280389/30086299-768509d0-9268-11e7-8e6b-626ac9ca512c.gif)| Dash uses [Plotly.js](https://github.com/plotly/plotly.js) for charting. About 50 chart types are supported, including maps. |
|![Financial report](https://user-images.githubusercontent.com/2678795/161153710-57952401-6e07-42d5-ba3e-bab6419998c7.gif)| Dash isn't just for dashboards. You have full control over the look and feel of your applications. Here's a Dash App that's styled to look like a PDF report. |

To learn more about Dash, read the [extensive announcement letter](https://medium.com/@plotlygraphs/introducing-dash-5ecf7191b503) or [jump in with the user guide](https://plotly.com/dash).

### Dash OSS & Dash Enterprise

With Dash Open Source, Dash apps run on your local laptop or workstation, but cannot be easily accessed by others in your organization.

Scale up with Dash Enterprise when your Dash app is ready for department or company-wide consumption. Or, launch your initiative with Dash Enterprise from the start to unlock developer productivity gains and hands-on acceleration from Plotly's team.

ML Ops Features: A one-stop shop for ML Ops: Horizontally scalable hosting, deployment, and authentication for your Dash apps. No IT or DevOps required.
- [**App manager**](https://plotly.com/dash/app-manager/) Deploy & manage Dash apps without needing IT or a DevOps team. App Manager gives you point & click control over all aspects of your Dash deployments.
- [**Kubernetes scaling**](https://plotly.com/dash/kubernetes/) Ensure high availability of Dash apps and scale horizontally with Dash Enterprise’s Kubernetes architecture. No IT or Helm required.
- [**No code auth**](https://plotly.com/dash/authentication/) Control Dash app access in a few clicks. Dash Enterprise supports LDAP, AD, PKI, Okta, SAML, OpenID Connect, OAuth, SSO, and simple email authentication.
- [**Job Queue**](https://plotly.com/dash/job-queue/) The Job Queue is the key to building scalable Dash apps. Move heavy computation from synchronous Dash callbacks to the Job Queue for asynchronous background processing.

Low-Code Features: Low-code Dash app capabilities that supercharge developer productivity.
- [**Design Kit**](https://plotly.com/dash/design-kit/) Design like a pro without writing a line of CSS. Easily arrange, style, brand, and customize your Dash apps.
- [**Snapshot Engine**](https://plotly.com/dash/snapshot-engine/) Save & share Dash app views as links or PDFs. Or, run a Python job through Dash and have Snapshot Engine email a report when the job is done.
- [**Dashboard Toolkit**](https://plotly.com/dash/toolkit/) Drag & drop layouts, chart editing, and crossfilter for your Dash apps.
- [**Embedding**](https://plotly.com/dash/embedding/) Natively embed Dash apps in an existing web application or website without the use of IFrames.

Enterprise AI Features: Everything that your data science team needs to rapidly deliver AI/ML research and business initiatives.
- [**AI App Marketplace**](https://plotly.com/dash/ai-and-ml-templates/) Dash Enterprise ships with dozens of Dash app templates for business problems where AI/ML is having the greatest impact.
- [**Big Data for Pything**](https://plotly.com/dash/big-data-for-python/) Connect to Python's most popular big data back ends: Dask, Databricks, NVIDIA RAPIDS, Snowflake, Postgres, Vaex, and more.
- [**GPU & Dask Acceleration**](https://plotly.com/dash/gpu-dask-acceleration/) Dash Enterprise puts Python’s most popular HPC stack for GPU and parallel CPU computing in the hands of business users.
- [**Data Science Workspaces**](https://plotly.com/dash/workspaces/) Be productive from Day 1. Write and execute Python, R, & Julia code from Dash Enterprise's onboard code editor.

See [https://plotly.com/contact-us/](https://plotly.com/contact-us/) to get in touch.

![Dash Enterprise](https://user-images.githubusercontent.com/2678795/161155614-21c54a22-f821-4dda-b910-ee27e27fb5f2.png)
