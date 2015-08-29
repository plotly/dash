
reactful api

start app:

backend supplies a message declaring:
- components
- the state of the components
- how the components depend on each other

```
[
    {
        'id': 'xdropdown',
        'componenttype': 'dropdown',
        // prop types
        'values': [
            {'label': 'Selection 1', 'value': 'sel1'},
            {'label': 'Selection 2', 'value': 'sel2'},
            {'label': 'Selection 3', 'value': 'sel3'}
        ],
        'dependson': []
    },
    {
        'id': 'ydropdown',
        'componenttype': 'dropdown',
        'values': ...
        'dependson':
    },
    {
        'id': 'xslider',
        'componenttype': 'slider',
        'min': ...,
        'max': ...,
        'value': ...,
        'dependson': ['xdropdown']
    },
    {
        'id': 'xslidervalue'
        'componenttype': 'div'
        'value': ...,
        'dependson': ['xslider']
    }
]
```

When an element changes state, all of the elements that depend on it will request the server for new values.

`dropdownx` changes from 'sel1' to 'sel2'

request:
```
{
    'children': ['xslider', 'ydropdown'] // redudant: the server should know this since it supplied the original values
    // the app state, expanded. Note that not all of the targets depend on the states listed below
    'parents': {
        'xdropdown':  {
            'id': 'xdropdown',
            ...
        },
        'ydropdown': {
            'id': '...',
            ...
        }
    }
}
```

response:
```
[
    {
        'id': 'xslider',
        'min': ...,
        'max': ...,
        'value': ...
    },
    {
        'id': 'ydropdown',
        ...
    }
]
```

This changes the state in the front-end, causing another request:

request:
```
{
    'target': 'xslidervalue',
    'state': [
        {
            'id': 'xslider',
            'value': ...
            'min': ...
        }
    ]
}
```

response:
```
{
    'id': 'xslidervalue',
    'content': ...
}
```

In Python, the view routes messages

@update
def():
    if 'target' == 'xslidervalue':
        ...

    if 'target' == 'xslider':






