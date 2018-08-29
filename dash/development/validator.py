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


def generate_validation_error_message(error_list, level=0, error_message=''):
    for e in error_list:
        curr = e.document_path[-1]
        message = DASH_ERROR_MESSAGES[e.code].format(
            *([''] * len(e.info)),
            constraint=e.constraint,
            value=e.value
        )
        new_line = (
            '  ' * level +
            ('[{0}]' if isinstance(curr, int) else '* {0}\t<- {1}')
            .format(curr, '' + message) + '\n'
        )
        error_message += new_line
        for nested_error_list in e.info:
            error_message = generate_validation_error_message(
                nested_error_list,
                level + 1,
                error_message)
    return error_message
