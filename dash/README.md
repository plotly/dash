### running a python example

The backend doesn't serve files (yet), it only responds to HTTP calls.

```
(dash2) $ cd dash
(dash2/dash) $ pip install -r requirements.txt
Collecting click==6.6 (from -r requirements.txt (line 1))
Collecting Flask==0.11 (from -r requirements.txt (line 2))
  Using cached Flask-0.11-py2.py3-none-any.whl
Collecting Flask-Cors==2.1.2 (from -r requirements.txt (line 3))
Collecting itsdangerous==0.24 (from -r requirements.txt (line 4))
...
...
Successfully installed Flask-0.11 Flask-Cors-2.1.2 Jinja2-2.8 MarkupSafe-0.23 Werkzeug-0.11.10 click-6.6 itsdangerous-0.24 numpy-1.11.0 pandas-0.18.1 plotly-1.11.0 python-dateutil-2.5.3 pytz-2016.4 requests-2.10.0 six-1.10.0

(dash2/dash) $ python helloworld.py
/Users/chriddyp/Repos/dash2/dash/vv/lib/python2.7/site-packages/flask/exthook.py:71: ExtDeprecationWarning:

Importing flask.ext.cors is deprecated, use flask_cors instead.

 * Running on http://127.0.0.1:8050/ (Press CTRL+C to quit)
 * Restarting with stat
/Users/chriddyp/Repos/dash2/dash/vv/lib/python2.7/site-packages/flask/exthook.py:71: ExtDeprecationWarning:

Importing flask.ext.cors is deprecated, use flask_cors instead.

 * Debugger is active!
 * Debugger pin code: 254-379-279
```
