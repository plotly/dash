
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/np-8/dash-uploader)&nbsp;![PyPI](https://img.shields.io/pypi/v/dash-uploader)&nbsp;![PyPI - Downloads](https://img.shields.io/pypi/dm/dash-uploader)&nbsp;![GitHub](https://img.shields.io/github/license/np-8/dash-uploader)

![upload large files with dash-uploader](https://github.com/np-8/dash-uploader/blob/0.2.0/docs/upload-demo.gif?raw=true)

# 📤 dash-uploader
The upload package for [Dash](https://dash.plotly.com/) applications using large data files. 

### 🏠 Homepage & Documentation
[https://github.com/np-8/dash-uploader](https://github.com/np-8/dash-uploader)


## Short summary
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 💾 Data file size has no limits. (Except the hard disk size)<bR>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ☎ Call easily a callback after uploading is finished.<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 📦 Upload files using [resumable.js](https://github.com/23/resumable.js) 
<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ✅ Works with Dash 1.1.0.+ & Python 3.6+. (Possibly with other versions, too)<br>



## Installing
```
pip install dash-uploader
```

## Usage


### Simple example

```python
import dash
import dash_html_components as html
import dash_uploader as du

app = dash.Dash(__name__)

# 1) configure the upload folder
du.configure_upload(app, r"C:\tmp\Uploads")

# 2) Use the Upload component
app.layout = html.Div([
    du.Upload(),
])

if __name__ == '__main__':
    app.run_server(debug=True)

```

