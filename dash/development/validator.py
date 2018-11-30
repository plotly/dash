from textwrap import dedent
import plotly
import cerberus


class DashValidator(cerberus.Validator):
    types_mapping = cerberus.Validator.types_mapping.copy()
    types_mapping.pop('list')  # To be replaced by our custom method
    types_mapping.pop('number')  # To be replaced by our custom method

    def _validator_plotly_figure(self, field, value):
        if not isinstance(value, (dict, plotly.graph_objs.Figure)):
            self._error(
                field,
                "Invalid Plotly Figure.")
        if isinstance(value, dict):
            try:
                plotly.graph_objs.Figure(value)
            except (ValueError, plotly.exceptions.PlotlyDictKeyError) as e:
                self._error(
                    field,
                    "Invalid Plotly Figure:\n\n{}".format(e))

    def _validator_options_with_unique_values(self, field, value):
        if not isinstance(value, list):
            self._error(field, "Invalid options: Not a list!")
        values = set()
        for i, option_dict in enumerate(value):
            if not isinstance(option_dict, dict):
                self._error(
                    field,
                    "The option at index {} is not a dictionary!"
                    .format(i)
                )
            if 'value' not in option_dict:
                self._error(
                    field,
                    "The option at index {} does not have a 'value' key!"
                    .format(i)
                )
            curr = option_dict['value']
            if curr in values:
                self._error(
                    field,
                    ("The options list you provided was not valid. "
                     "More than one of the options has the value {}."
                     .format(curr))
                )
            values.add(curr)

    def _validate_type_list(self, value):
        if isinstance(value, (list, tuple)):
            return True
        # These types can be cast to list
        elif isinstance(value, (self.component_class, str, set)):
            return False
        # Handle numpy array / pandas series
        try:
            value_list = list(value)
            if isinstance(value_list, list):
                return True
        except (ValueError, TypeError):
            pass
        return False

    # pylint: disable=no-self-use
    def _validate_type_number(self, value):
        if isinstance(value, (int, float)):
            return True
        if isinstance(value, str):  # Since int('3') works
            return False
        # The following handles numpy numeric types
        try:
            int(value)
            return True
        except (ValueError, TypeError, AttributeError):
            pass
        try:
            float(value)
            return True
        except (ValueError, TypeError, AttributeError):
            pass
        return False

    @classmethod
    def set_component_class(cls, component_cls):
        cls.component_class = component_cls
        c_type = cerberus.TypeDefinition('component', (component_cls,), ())
        cls.types_mapping['component'] = c_type
        d_type = cerberus.TypeDefinition('dict', (dict,), ())
        cls.types_mapping['dict'] = d_type


def parse_cerberus_error_tree(errors, level=0, error_message=''):
    for prop, error_tuple in errors.items():
        error_message += (' ' * level) + '* {}'.format(prop)
        if len(error_tuple) == 2:
            error_message += '\t<- {}\n'.format(error_tuple[0])
            error_message = parse_cerberus_error_tree(
                error_tuple[1],
                level + 1,
                error_message)
        else:
            if isinstance(error_tuple[0], str):
                error_message += '\t<- {}\n'.format(error_tuple[0])
            elif isinstance(error_tuple[0], dict):
                error_message = parse_cerberus_error_tree(
                    error_tuple[0],
                    level + 1,
                    error_message + "\n")
    return error_message


def generate_validation_error_message(errors, level=0, error_message=''):
    error_message = parse_cerberus_error_tree(errors, level, error_message)
    error_message += dedent("""
        You can turn off these validation exceptions by setting
        `app.config.suppress_validation_exceptions=True`
    """)
    return error_message
