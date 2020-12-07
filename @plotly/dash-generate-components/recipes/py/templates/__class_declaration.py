class ${key.split('/').slice(-1)[0].split('.')[0]}(Component):
    """A ${key.split('/').slice(-1)[0].split('.')[0]} component.
${target.description}

Keyword arguments:
${templates.class_property(js.core.filterProps(target.props))}"""
    @_explicitize_args
    def __init__(self, ${templates.children_default_arg(!!target.props.children)}${templates.class_parameter(js.core.filterPropsNoChildren(target.props))}, **kwargs):
        self._prop_names = [${templates.children(!!target.props.children)}${templates.class_property_name(js.core.filterPropsNoChildren(target.props))}]
        self._type = '${key.split('/').slice(-1)[0].split('.')[0]}'
        self._namespace = '${recipe.vars.py_name}'
        self._valid_wildcard_attributes = []
        self.available_properties = [${templates.children(!!target.props.children)}${templates.class_property_name(js.core.filterPropsNoChildren(target.props))}]
        self.available_wildcard_properties = []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument \`' + k + '\` was not specified.')
        super(${key.split('/').slice(-1)[0].split('.')[0]}, self).__init__(${templates.children_arg(!!target.props.children)}**args)