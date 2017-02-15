## Testing

```
$ ag -l --python | entr python -m unittest discover -s tests/
```

***

## Dash python backend

The backend doesn't serve files (yet), it only responds to HTTP calls from the web cloent. See [main README.md](../README.md) for instructions on running a local development web server.

### running a python example

```
(dash2) $ cd dash
(dash2/dash) $ pip install -r requirements.txt
Collecting click==6.6 (from -r requirements.txt (line 1))
Collecting Flask==0.11 (from -r requirements.txt (line 2))
...
Successfully installed Flask-0.11 Flask-Cors-2.1.2 Jinja2-2.8 MarkupSafe-0.23 Werkzeug-0.11.10 click-6.6 itsdangerous-0.24 numpy-1.11.0 pandas-0.18.1 plotly-1.11.0 python-dateutil-2.5.3 pytz-2016.4 requests-2.10.0 six-1.10.0

(dash2/dash) $ python helloworld.py

 * Running on http://127.0.0.1:8050/ (Press CTRL+C to quit)
 * Debugger is active!
 * Debugger pin code: 254-379-279
```


### Python Developer guide

#### Use `virtualenv`

Running everything in the same virtual environment ensures that you don't have
conflicts with other globally installed python packages, and in general makes
for a much more consistent development environment. You could also create
multiple virtualenvs for different versions of Dash, for instance.

##### Install the goods

```sh
$ pip install virtualenv
$ pip install virtualenvwrapper
```

##### Add to your shell's configuration

```sh
# The actual file to edit will vary depending
# on your OS, shell, and setup.
$ vi ~/.bash_profile

# Add these lines
export WORKON_HOME=$HOME/.py_virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
```

##### Create a virtual environment

`my-dash-env` is a name of your choosing.

```sh
$ mkvirtualenv my-dash-env
```

##### Now you can switch to this virtual environment:

```sh
$ workon my-dash-env
```

More reading
- http://docs.python-guide.org/en/latest/dev/virtualenvs/


#### Debugging

Install `ipdb`:

```sh
$ pip install ipdb
```

Insert a breakpoint in your Python code:

```py
import ipdb; ipdb.set_trace()
```

More reading
- Intro: https://www.safaribooksonline.com/blog/2014/11/18/intro-python-debugger/
- Cheat sheet: http://georgejhunt.com/olpc/pydebug/pydebug/ipdb.html
- API: https://pypi.python.org/pypi/ipdb
