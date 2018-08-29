import plotly
import cerberus


def _merge(x, y):
    z = x.copy()
    z.update(y)
    return z


DASH_ERROR_MESSAGES = _merge(
    cerberus.errors.BasicErrorHandler.messages,
    {
        0x101: "Invalid Plotly Figure"
    }
)


class DashValidator(cerberus.Validator):
    def _validator_plotly_figure(self, field, value):
        try:
            plotly.graph_objs.Figure(value)
        except ValueError:
            error = cerberus.errors.ValidationError(
                document_path=self.document_path + (field,),
                schema_path=self.schema_path,
                code=0x101,
                rule="Plotly Figure must be valid!",
                constraint="https://plot.ly/javascript/reference",
                value=value,
                info=()
            )
            self._error([error])

    @classmethod
    def set_component_class(cls, component_cls):
        c_type = cerberus.TypeDefinition('component', (component_cls,), ())
        cls.types_mapping['component'] = c_type
        d_type = cerberus.TypeDefinition('dict', (dict,), ())
        cls.types_mapping['dict'] = d_type


def generate_validation_error_message(errors, level=0, error_message=''):
    for prop, error_tuple in errors.items():
        error_message += (' ' * level) + '* {}'.format(prop)
        if len(error_tuple) == 2:
            error_message += '\t<- {}\n'.format(error_tuple[0])
            error_message = generate_validation_error_message(
                error_tuple[1],
                level + 1,
                error_message)
        else:
            if isinstance(error_tuple[0], str):
                error_message += '\t<- {}\n'.format(error_tuple[0])
            elif isinstance(error_tuple[0], dict):
                error_message = generate_validation_error_message(
                    error_tuple[0],
                    level + 1,
                    error_message + "\n")
    return error_message
