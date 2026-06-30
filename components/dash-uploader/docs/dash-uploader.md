

#  dash-uploader
To use the Upload component you need to two things
- Configure dash-uploader with [`du.configure_upload`](#duconfigure_upload)
- Create the upload component with [`du.Upload`](#duupload)

Typically you also would like to define [callbacks](#3-callbacks) (functions that are called automatically when upload finishes).

> ⚠️**Security note**: The Upload component allows uploads of arbitrary files to the server harddisk and one should take this into account (with user token checking etc.) if used as part of a public website! Particularly, the `configure_upload` opens a route for `POST` HTTP requests. Use the [`http_request_handler`](#http_request_handler--none-or-subclass-of--duhttprequesthandler) argument for defining your custom validation logic.


# Table of contents

[1 Configuring dash-uploader](#1-configuring-dash-uploader)
- [`du.configure_upload`](#duconfigure_upload)

[2 Creating Upload components](#2-creating-upload-components)
- [`du.Upload`](#duupload)

[3 Callbacks](#3-callbacks)
- [`@du.callback`](#ducallback)
- [`@app.callback`](#appcallback)
 
[4 Custom handling of HTTP Requests](#4-custom-handling-of-http-requests)
- [`du.HttpRequestHandler`](#duhttprequesthandler)

[5 How dash-uploader works internally?](#5-how-dash-uploader-works-internally)

-----

## 1 Configuring dash-uploader

You need to configure the dash uploader after you created your dash application instance (`app`) and before you create any Upload components

**Example**
```python
import dash_uploader as du

du.configure_upload(app, r'C:\tmp\uploads')
```

### `du.configure_upload`

```python
configure_upload(app, folder, use_upload_id=True, upload_api=None, http_request_handler=None)
```

#### app: dash.Dash
The application instance. Usually created using
```python
app = dash.Dash(__name__)
```

#### folder: str
The folder where to upload files.  Can be relative 
(`"uploads"`) or absolute (`r"C:\tmp\my_uploads"`).
If the folder does not exist, it will be created
automatically.

#### use_upload_id: bool (Default: True)
Determines if the uploads are put into
folders defined by a "upload id". To define an upload id, use the `upload_id` parameter of the `du.Upload` component. In typical use case, upload id's are unique for different users. In that case, you must use a callable as the `app.layout`.

If True, uploads will be put into `<folder>/<upload_id>/`;
that is, every user (for example with different 
session id) will use their own folder. If False, 
all files from all sessions are uploaded into
same folder (not recommended).

#### upload_api: None or str
The upload api endpoint to use; the url that is used
internally for the upload component POST and GET HTTP
requests. For example, using `upload_api="/API/dash-uploader"` would create api endpoint and use address

```
http://<myhost>[<requests_pathname_prefix>]/API/dash-uploader
```
for the communication between the front-end and the server. The `requests_pathname_prefix` is added automatically, if the dash `app` instance has `requests_pathname_prefix`. (used with proxies)

#### http_request_handler:  None or subclass of du.HttpRequestHandler
*New in version **0.5.0***

Used for custom configuration on the HTTP POST and GET requests. This can be used to add validation for the HTTP requests (⚠️Important
if your site is public!). If None, dash_uploader.HttpRequestHandler is used.
If you provide a class, use a subclass of `du.HttpRequestHandler`.
See the documentation of [`@du.HttpRequestHandler`](#duhttprequesthandler) for
more details.


## 2 Creating Upload components
### `du.Upload`
Below are the arguments for the `du.Upload` component and their default values.
```python
Upload(
    id='dash-uploader',
    text='Drag and Drop Here to upload!',
    text_completed='Uploaded: ',
    text_disabled='The uploader is disabled.',
    cancel_button=True,
    pause_button=False,
    disabled=False,
    filetypes=None,
    max_file_size=1024,
    chunk_size=1,
    default_style=None,
    upload_id=None,
    max_files=1,
)
```

#### id: str (default: 'dash-uploader')
The html id for the component. This is needed when defining callbacks. Note that ids must be unique in a dash application.

#### text: str (Default: ''Drag and Drop Here to upload!')
The text to be shown in the upload "Drag
and Drop" area. Optional.

#### text_completed: str
The text to show in the upload area 
after upload has completed succesfully before
the name of the uploaded file. 

For example, if user
uploaded "data.zip" and `text_completed` is 
"Ready! ", then user would see text "Ready! 
data.zip".

#### text_disabled: str
*New in version **[0.6.0]***

The text to show in the upload area when the
the component is disabled.

#### cancel_button: bool
If True, shows a cancel button.

#### pause_button: bool
If True, shows a pause button.

#### disabled: bool
*New in version **[0.6.0]***

If True, the file is not allowed to be uploaded.

#### filetypes: list of str or None
The filetypes that can be uploaded. 
For example `['zip', 'rar']`.
Note that this just checks the extension of the 
filename, and user might still upload any kind 
of file (by renaming)!
By default, all filetypes are accepted.

#### max_file_size: numeric
The maximum file size in Megabytes. Default: 1024 (=1Gb).

#### chunk_size: numeric
*New in version **[0.6.0]***

The chunk size in Megabytes. Optional. Default: 1 (=1Mb).

#### default_style: None or dict
Inline CSS styling for the main div element. 
If None, use the default style of the component.
If dict, will use the union on the given dict
and the default style. (you may override
part of the style by giving a dictionary)
More styling options through the CSS classes.

#### upload_id: None or str
The upload id, created with `uuid.uuid1()` or uuid.uuid4(), for example. If `None`, creates random session id with `uuid.uuid1()`.  Defines a subfolder where the files are to be uploaded.

Only used, if `use_upload_id` parameter is set to `True` in [`du.configure_upload`](#duconfigure_upload). 

#### max_files: int (default: 1)
>⚠️ **Experimental** feature. Read below. For bulletproof
implementation, force usage of zip files and keep
max_files = 1.

The number of files that can be added to 
the upload field simultaneously.

**Notes**: <br>
**(1)** If even a single file which is not supported file
    type (i.e. missing in  `filetypes`), is added to the upload queue, upload process of all files will be permanently interrupted. <br>
**(2)** Use reasonably small number in `max_files`. <br>
**(3)** When uploading two (or more) folders with Chrome, there is 
    a bug in resumable.js which makes only one of the
    folders to be uploaded. See:
    https://github.com/23/resumable.js/issues/416<br>
**(4)** When uploading folders, note that the subdirectories
    are **not** created -> All files in the folders will
    be uploaded to the single upload folder.<br>



## 3 Callbacks

Callbacks can be defined using two different approaches
- `@du.callback`: short notation, for typical use cases
- `@app.callback`: needs more verbose code. In case you need more control than when using the `@du.callback`.


In the following example it is assumed that the `du.Upload` component id is `dash-uploader`, i.e. the component was created with:

```
du.Upload(
    id='dash-uploader',
)
```

###  `@du.callback`

*New in version **0.3.0***

Easiest way to call a simple callback after uploading would be something like:

```python
@du.callback(
    output=Output('callback-output', 'children'),
    id='dash-uploader',
)
def get_a_list(filenames):
    return html.Ul([html.Li(filenames)])
```

The syntax is
```python
@du.callback(
    output=<Output>,
    id=<Upload_id>,
)
def call_me(filenames):
    # Do some processing
    return <Dash component>
```

#### output: dash.dependencies.Output
This is the Output object, just as in regular [dash callbacks](https://dash.plotly.com/basic-callbacks).

#### id: str
This must be the same `id` as used when initiating your `du.Upload` component.

#### call_me: function
A function that takes exactly one argument: `filenames`.

#### filenames: list of str
A list of strings. These will be the uploaded files. For example: 
`['C:\tmp\Uploads\166d6f24-a80d-11ea-aa00-f48c5012fb50\dataset.csv']`

#### Dash component
The return value of the `call_me` should be a dash component, as in the regular [dash callbacks].


### `@app.callback`

This method needs more verbose code and it is the conventional "[dash way]((https://dash.plotly.com/basic-callbacks))" to create a callback.  Use this if `@du.callback` does not give you enough control.

The syntax can be seen in the following example
```python
@app.callback(
    Output('callback-output', 'children'),
    [Input('dash-uploader', 'isCompleted')],
    [State('dash-uploader', 'fileNames'),
     State('dash-uploader', 'upload_id')],
)
def callback_on_completion(iscompleted, filenames, upload_id):
    if not iscompleted:
        return

    out = []
    if filenames is not None:
        if upload_id:
            root_folder = Path(UPLOAD_FOLDER_ROOT) / upload_id
        else:
            root_folder = Path(UPLOAD_FOLDER_ROOT)

        for filename in filenames:
            file = root_folder / filename
            out.append(file)
        return html.Ul([html.Li(str(x)) for x in out])

    return html.Div("No Files Uploaded Yet!")
```

#### du.Upload properties used
- `isCompleted`: boolean flag indicating if uploading has been completed. 
- `fileNames`: List of strings of the filenames or None. This does not have the upload folder or the upload_id in it. 
- `upload_id`: The upload id used when initiating the `du.Upload` component.


## 4 Custom handling of HTTP Requests
### `du.HttpRequestHandler`
*New in version **0.5.0***

The `HttpRequestHandler` is a class that is meant to be subclassed. It is used as an argument for [`configure_upload`](#duconfigure_upload), and it makes custom HTTP POST and GET request handling possible. For example, if you run your dash app publicly, you should use some validation logic to validate the HTTP requests from the users!


#### Example of a subclass

```python
class HttpRequestHandler(BaseHttpRequestHandler):
    # You may use the flask.request
    # and flask.session inside the methods of this
    # class when needed.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def post_before(self):
        pass

    def post(self):
        self.post_before()
        returnvalue = super().post()
        self.post_after()
        return returnvalue

    def post_after(self):
        pass

    def get_before(self):
        pass

    def get(self):
        self.get_before()
        returnvalue = super().get()
        self.get_after()
        return returnvalue

    def get_after(self):
        pass
```

#### How does this all work?

- The React Component of `dash-uploader` sends HTTP POST requests. It could in the future send also HTTP GET requests, or other HTTP requests.
- The Flask server (Dash uses Flask underneath) is configured in [`configure_upload`](#duconfigure_upload) to call the `post()` function of the `http_request_handler` on every HTTP POST request directed to the API endpoint of the dash-uploader.
- The values in the POST request are listed in [Documentation of resumable.js](https://github.com/23/resumable.js#how-do-i-set-it-up-with-my-server). Most interesting from these is probably the filename (`resumableFilename`).  In addition to these, there is `upload_id` added by the `dash-uploader`, if `use_upload_id=True` when calling [`configure_upload`](#duconfigure_upload).
- You can use the [flask.request](https://flask.palletsprojects.com/en/1.1.x/api/#flask.request) and [flask.session](https://flask.palletsprojects.com/en/1.1.x/api/#flask.session) proxies as you like. There you get access to all the HTTP Request parameters and Cookies, for example. As an quick example, to get the request filename, upload_id and some cookie value, you can use:

```python
from flask import request 

filename = request.form.get("resumableFilename", default="error", type=str)
upload_id = request.form.get("upload_id", default="", type=str)
cookie_value = request.cookies.get('some_cookie')
```

## 5 How dash-uploader works internally?

- Please refer to the [developer documentation](./CONTRIBUTING.md#7--how-does-dash-uploader-work-internally) for the details.
