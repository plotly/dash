# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class LogoutButton(Component):
    """A LogoutButton component.
Logout button to submit a form post request to the `logout_url` prop.
Usage is intended for dash-deployment-server authentication.

DDS usage:

`dcc.LogoutButton(logout_url=os.getenv('DASH_LOGOUT_URL'))`

Custom usage:

- Implement a login mechanism.
- Create a flask route with a post method handler.
`@app.server.route('/logout', methods=['POST'])`
  - The logout route should perform what's necessary for the user to logout.
  - If you store the session in a cookie, clear the cookie:
  `rep = flask.Response(); rep.set_cookie('session', '', expires=0)`

- Create a logout button component and assign it the logout_url
`dcc.LogoutButton(logout_url='/logout')`

See https://dash.plot.ly/dash-core-components/logout_button
for more documentation and examples.

Keyword arguments:
- id (string; optional): Id of the button.
- label (string; optional): Text of the button
- logout_url (string; optional): Url to submit a post logout request.
- style (dict; optional): Style of the button
- method (string; optional): Http method to submit the logout form.
- className (string; optional): CSS class for the button.

Available events: """
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, label=Component.UNDEFINED, logout_url=Component.UNDEFINED, style=Component.UNDEFINED, method=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'label', 'logout_url', 'style', 'method', 'className']
        self._type = 'LogoutButton'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_events = []
        self.available_properties = ['id', 'label', 'logout_url', 'style', 'method', 'className']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(LogoutButton, self).__init__(**args)

    def __repr__(self):
        if(any(getattr(self, c, None) is not None
               for c in self._prop_names
               if c is not self._prop_names[0])
           or any(getattr(self, c, None) is not None
                  for c in self.__dict__.keys()
                  if any(c.startswith(wc_attr)
                  for wc_attr in self._valid_wildcard_attributes))):
            props_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self._prop_names
                                      if getattr(self, c, None) is not None])
            wilds_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self.__dict__.keys()
                                      if any([c.startswith(wc_attr)
                                      for wc_attr in
                                      self._valid_wildcard_attributes])])
            return ('LogoutButton(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                'LogoutButton(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')
