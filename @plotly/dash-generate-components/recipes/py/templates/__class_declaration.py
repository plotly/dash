class ${target.displayName}(Component):
"""A ${target.displayName} component.
${target.description}

Keyword arguments:
${templates.class_property(js.core.filterProps(target.props))}
"""
@_explicitize_args
def __init__(self, ${templates.class_parameter(js.core.filterProps(target.props))}, **kwargs):
    self._prop_names = [${templates.class_property_name(js.core.filterProps(target.props))}]
    self._type = '${target.displayName}'
    self._valid_wildcard_attributes = []
    self.available_properties = [${templates.class_property_name(js.core.filterProps(target.props))}]
    self.available_wildcard_properties = []

    _explicit_args = kwargs.pop('_explicit_args')
    _locals = locals()
    _locals.update(kwargs)  # For wildcard attrs
    args = {k: _locals[k] for k in _explicit_args if k != 'children'}

    for k in []:
    if k not in args:
        raise TypeError(
        'Required argument \`' + k + '\` was not specified.')
    super(${target.displayName}, self).__init(**args)