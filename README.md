dash is a framework for making static and dynamic user interfaces that can connect to technical computing backends.

See the [dash 2.0 announcement](https://github.com/plotly/dash) for more context.

#### Prototype

Kick dem tires! See what its all about!

http://plotly-dash.herokuapp.com

#### Development

1. A messy prototype has been written in [@chriddyp/messin](https://github.com/chriddyp/messin) with docs and examples deployed on heroku at http://plotly-dash.herokuapp.com. Also, [dashboards.ly](https://dashboards.ly) (code at [@plotly/dashboards.ly](https://github.com/plotly/dashboards.ly)) contains some drag-and-droppable and editable interaction that dash's edit mode should mimic.

2. **(current phase)** - rewrite an alpha prototype in this repository (1 month)

3. Rewrite the alpha prototype as a public beta. I imagine that each of the components of dash (the front end, the python back end, suites of react components) will be published as separate repositories under [@plotly](https://github.com/plotly) or a new organization `dash`.

#### Community
Join the chat room at [https://dash-talk.slack.com/signup](https://dash-talk.slack.com/signup). Feel free to send the distribute the invite.


## Architecture

dash is composed of several parts:

[A - JSON API](#a---json-api-for-describing-components-layout) that describes the layout and composition of the web applications

[B - HTTP API](#b---http-api-for-updating-components) that specifies how components depend on each other and how components should update when the front-end state changes

[C - Front-end implementation](#c---front-end-implementation-the-renderer) of these APIs written with React and redux ([`./renderer`](https://github.com/plotly/dash2/tree/master/renderer)) that can render components that are supplied to it and thread actions and event handlers into the components.

[D - Suites of components](#d---suites-of-components) e.g. components for creating dashboards, components for creating reports, components for creating slides.

[E - React editing interface](#e---react-editing-interface) for adding new items to interface and maybe ability to edit items in the tree

[F - Back-end implementation](#f---backend-implementation) of the HTTP API written with Python and Flask

This repo contains prototypes of these pieces.


### A - JSON API for describing components (`layout`)

The layout and composition of the applications is described and serialized as JSON.

This object is herein defined as the "`layout`".

Each component in the interface has a specific `type`, a set of properties `props`, its own content or set of children.

All native HTML components, e.g. `<div>`, `<h1>`, `<img>`, `<iframe>` are supported. All of their HTML attributes, like `class`, `id`, `style` are supported as `props`.

```javascript
{
    type: "div",
    props: {
        id: "parent-div",
        style: {
            backgroundColor: 'lightgrey' // distinction with HTML: style properties are camelCased
        }
    },
    children: [
        {
            type: "img",
            props: {
                src: "https://plot.ly/~chris/1638.png"
            }
        }
    ]
}
```

describes the HTML
```javascript
<div id="parent-div" style="background-color: lightgrey">
    <img src="https://plot.ly/~chris/1638.png"/>
</div>
```

Higher-level components can also be specified in this specification. The front-end is responsible for understanding the component types and knowing how to render them.

For example, a plotly graph might be described as:

```javascript
{
    type: "PlotlyGraph",
    props: {
        figure: {
            data: [
                {x: [1, 2, 3], y: [4, 1, 6], type: 'scatter'},
                {x: [1, 2, 3], y: [2, 3, 9], type: 'bar'}
            ]
        }
    }
}
```

which, if available in the front-end component registry, would rendered using the `plotly.js` library.

In `dash`'s "edit-mode", users should be able to rearrange, resize, and delete components. Components opt-in to this behavior. These behaviors are seralized as optional `props`:
- `resizable`: whether or not the component can be resized
- `droppable`: whether or not components can be dragged and dropped into this component (i.e. whether or not is a "drop zone")
- `draggable`: whether or not this component can be dragged and dropped onto other components
- `deletable`: whether or not this component can be removed

The actual resizing, dragging and dropping, and deleting behavior is determined by the actual front-end implementation. The actual UI that displays and triggers these events is the responsibility of the components themselves.

Additionally, certain components depend on each other. For example, a graph might depend on a slider; a table might depend on a search box; zooming into a graph might update a secondary graph. These relationships are described through a property `"dependencies"` which is a list of IDs that the component depends on. For example:

```javascript
{
    type: "div",
    children: [
        {
            type: "dropdown",
            props: {
                id: "dropdown-1"
            }
        },
        {
            type: "dropdown",
            props: {
                id: "dropdown-2",
                dependencies: ["dropdown-1"]
            }
        },
        {
            type: "PlotlyGraph",
            props: {
                dependencies: ["dropdown-1", "dropdown-2"]
            }
        }
    ]
}
```

In this case, the plotly graph depends on "dropdown-1" and "dropdown-2" and "dropdown-2" depends on "dropdown-1". This spec does not describe *how* a component depends on another, it merely states the relationship.
A dependency means that whenever a component changes state (i.e. when a user enters text into a text box or a dropdown item gets selected), it will make an HTTP call to the server with its new state and the server will respond with the updated state of the dependent components. Each component will be handed this server-calling action, and will be responsible for firing it when its state changes.

##### Uncertainties
- `children` type.

Array of objects is definitely supported:
```js
{
    type: "div",
    children: [
        {
            type: "div"
        },
        {
            type: "div"
        }
    ]
}
```

And a `string` for simple text content inside a component should also be allowed, right?
```js
{
    type: "div",
    children: "text inside a div"
}
```

Should we allow single objects?
```js
{
    type: "div",
    children: {
        type: "div"
    }
}
```

- The mechanics of `resizable`, `draggable`, `droppable`, `deletable` are still a little fuzzy to me. We may need more information to serialize these behaviors.

- Is this spec missing anything?

### B - HTTP API for updating components

Two types of requests are made.

**Initialization**
`GET /initialization`
Retrieve the "`layout`" JSON that describes the application

**Component Updating**
`POST /component-update`
When a component changes state and has dependent components, make a request to the server with the new state of that component and retrieve a response containing the desired state of the dependent components.

**Example 1 - One component that has two dependents**

JSON layout:
```js
{
    type: "div",
    children: [
        {
            type: "dropdown",
            props: {
                id: "dropdown-1",
                value: "oranges",
                options: [
                    {label: "Apples", value: "apples"},
                    {label: "Oranges", value: "oranges"}
                ]
            }
        },

        {
            type: "PlotlyGraph",
            props: {
                id: "my-graph",    
                figure: {...}
            },
            dependencies: ["dropdown-1"]
        },

        {
            type: "p",
            id: "caption",
            children: "selected value of the dropdown is 'oranges'",
            dependencies: ["dropdown-1"]
        }
    ]
}
```

When "dropdown-1" changes, this request is made:
```
{
    id: "dropdown-1",
    oldProps: {
        value: "apples",
        options: [
            {label: "Apples", value: "apples"},
            {label: "Oranges", value: "oranges"}
        ]
    },
    newProps: {
        value: "oranges",
        options: [
            {label: "Apples", value: "apples"},
            {label: "Oranges", value: "oranges"}
        ]
    }    
}
```

And this is an example of the response:
```
[
    {
        id: "my-graph",
        props: {
            figure: {
                layout: {...},
                data: [...]
            }
        }
    },
    {
        id: "caption",
        children: "new value of the dropdown is 'apples'"
    }
]
```

**Example 2 - One component depends on two components**
When a component changes, the request must contain the state of *all* of the components that the dependent components depend on, not just the component that changed.

For example, if a graph depends on the values of two dropdowns, the state of both of the dropdowns must be sent in the request to the server.

Example "`layout`":
```
[
    type: "div",
    children: [
        {
            type: "Dropdown",
            props: {id: "dropdown-1"}
        },
        {
            type: "Dropdown",
            props: {id: "dropdown-2"}
        },
        {
            type: "PlotlyGraph",
            props: {id: "graph-1"}
            dependencies: ["dropdown-1", "dropdown-2"]
        }
    ]
]
```

When `"dropdown-1"` or `"dropdown-2"` change, a request is made to the server containing both of their state. For example, if `"dropdown-1"` changed this request would be made:

```
[
    {
        id: "dropdown-1",
        newProps: {...},
        oldProps: {...}
    },
    {
        id: "dropdown-2",
        props: {...} // just "props" not "newProps"/"oldProps" because nothing changed
    }
]
```

with a response like:
```
[
    {
        id: "graph-1",
        props: {
            figure: {...}
        }
    }
]
```

##### Uncertainties
- What should the URL names be? should we prefix them with e.g. `dash-` so that they don't interfere with other servers that might be running? should they be configurable?
- Do we need to send *all* of the props? What happens when the props are huge, like figure objects or tables? Should the define spec determine which props are necessary?
- How do actions that aren't state changes fit into this? For example, clicking on a button.
- Sometimes the backend needs to update the front end, e.g. when data gets pushed to a database, when an experiment finishes, or on some timed event. Maybe we should we define an additional persistent websocket connection to handle these cases?

### C - Front-End Implementation (the `"renderer"`)

```
import Renderer from 'dash-renderer.js'
import xhr from 'xhr.js'

const layout = xhr.GET('/initialization')

<Renderer layout={layout}/>
```

The front-end implementation is responsible for:
- rendering the components specified from the `layout`
- providing HTTP request trigger actions into components's `onChange` handlers (for the components that have dependents)
- providing `resize`, `rearrange`, `delete`, and `edit` actions to components that will appropriately update the app's component tree and state
- providing HTTP response handling
- providing loading and error states to the appropriate components

The front-end doesn't actually contain any presentational components. The developer is responsible for "registering" the set of components that they need (as specified through the "type" property of the objects in `layout`):

```
// registry.js

import {
    PlotlyGraph,
    Dropdown,
    Slider
} from 'dash-basic-component-suite.js'

module.exports = {PlotlyGraph, Dropdown, Slider};
```

It passes actions and props into the components through element cloning and container elements.

For example, if a component in the spec is "editable", then an `onEdit` or an `onChange` action that updates the appropriate prop of that component in the app's `layout` state. See `renderTree.js` and `EditableContent.react.js` for an example and the [Redux chapter on container components](http://redux.js.org/docs/basics/UsageWithReact.html).

Similarly, components that are `"draggable"` or `"droppable"` will be wrapped in store-connected action-bound drag-and-drop containers.

Our goal is to make it as easy as possible to plug-in presentational components. The presentational components should be totally unaware of the actual actions that need to be fired when they get re-arranged, deleted, or edited.

So, our `renderer.js` must also define a set of `props` that it may inject into the presentational components. The presentational components should be aware of `renderer.js`'s intentions of these props and actions and render or fire the functions appropriately. This list of props include:
- `onPropUpdate` - if e.g. a text field is editable, then `onPropUpdate` should get called when the value of the text field changes. In this case, the value of the text field is assumed to be a `prop` of that component. If that component has any dependents, then this action will also make an HTTP call to `/component-update` with the new values.
- `onDrop`, `onDrag` - actions that appropriately update the `layout` state when items get dragged and dropped
- `isHovering` - prop that informs the appropriate components when they are actively being dragged (or when a drag event is happening?)
- `onResize` - if the component is resizable, then this action should be called when it gets resized so that `renderer.js` can appropriately resize the other components by threading around new sets of `width` and `height`
- `width` and `height`
- `deleteItem` - action that the component tie to its deleting interface (e.g. clicking on an `x` in the corner of an item)
- `isLoading` - if the `/update-component` request is pending for this component then it is in a loading state and should display that state to the user in some way (local loading states)
- `error` - if the `/update-component` request has failed for this component then it is an error state and it should display that state to the user in some way (local error states)

For a React component to be a fully functional member of `dash`, it just needs to be able to accept these properties as `props` and render and bind accordingly.

##### Uncertainties
- How will the `registry` work? How can get users to define components in the registry without having to write any JS (e.g. from pure python)?
- The requirements to get resizing and dragging and dropping to work is pretty hazy... not sure what needs to get passed around to the components to make this work

### D - Suites of Components

`renderer.js` won't contain any actual presentational components. It will be able to render all of the built-in HTML elements and any components that are defined by the developer in the `Registry`.

Users will import (or develop their own) suites of components different types of apps. These suites include:
- A web-layout basics suite: [some type of grid abstraction](http://arnaudleray.github.io/pocketgrid/docs/#creating-rows-and-columns-the-cool-way)
- A suite of high level controls: sliders, dropdowns, text inputs, radio items
- A plotly graph component
- A dashboarding suite: dashboard header; dashboard graph containers; editable text, titles, and labels; big bold indicators; light tables
- A reporting suite: A nice title element, nice editable `h1`-`h6`, `pre`, `div`, and `p` tags
- A suite for creating slides and presentations
- Maybe a suite for creating infographics?


##### Uncertainties
- Do suites include CSS stylesheets? Or just pure inline CSS?
- How will the registry work?

### E - React editing interface

### F - Backend implementation

The backend will be responsible for:
- Responding to the HTTP requests
- Describing the `layout` in a pythonic way
- Providing an intuitive interface for registering and defining the dependency callbacks
- Exposing the underlying `flask` server so that users can benefit from that ecosystem for things like HTTP Auth, etc.

I think the interface presented in [@chriddyp/messin prototype](https://github.com/chriddyp/messin) (example: [http://ploty-dash.herokuapp.com](http://ploty-dash.herokuapp.com)) is really nice.

##### Uncertainties
- What do other folks think about the pythonic interface in example: [http://ploty-dash.herokuapp.com](http://ploty-dash.herokuapp.com)
- How will the registry of front-end components work?
- Can we export `PropTypes` so that we can do back-end prop validation?
- How can we distribute this via pip?
- Where does the `index.html` and the `dash-bundle.js` go? How is it distributed? How do folks import (or bundle) their own JS? Do we create something like `yoeman` and template generators?
- How can we make this work really nicely in jupyter (iframe)? How can that work with flask's `debug=True` auto-reloading magic?
- How should we support multi-page apps? [http://ploty-dash.herokuapp.com](http://ploty-dash.herokuapp.com) is actually a dash app itself, but I *think* supporting multiple pages became sort of messy
