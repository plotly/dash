import plotly
import cerberus


class DashValidator(cerberus.Validator):
    def _validator_plotly_figure(self, field, value):
        if not isinstance(value, (dict, plotly.graph_objs.Figure)):
            self._error(
                field,
                "Invalid Plotly Figure: Not a dict")
        if isinstance(value, dict):
            try:
                plotly.graph_objs.Figure(value)
            except (ValueError, plotly.exceptions.PlotlyDictKeyError) as e:
                self._error(
                    field,
                    "Invalid Plotly Figure:\n\n{}".format(e))

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
