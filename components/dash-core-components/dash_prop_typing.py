# This file is automatically loaded on build time to generate types.

def generate_plotly_figure(*_):
    return "typing.Union[Figure, dict]"


def generate_datetime_prop(array=False):

    def generator(*_):
        datetime_type = "typing.Union[str, datetime.datetime]"
        if array:
            datetime_type = f"typing.Sequence[{datetime_type}]"
        return datetime_type

    return generator


custom_imports = {
    "Graph": ["from plotly.graph_objects import Figure"],
    "DatePickerRange": ["import datetime"],
    "DatePickerSingle": ["import datetime"],
}

custom_props = {
    "Graph": {"figure": generate_plotly_figure},
    "DatePickerRange": {
        "start_date": generate_datetime_prop(),
        "end_date": generate_datetime_prop(),
        "min_date_allowed": generate_datetime_prop(),
        "max_date_allowed": generate_datetime_prop(),
        "disabled_days": generate_datetime_prop(True),
    },
    "DatePickerSingle": {
        "date": generate_datetime_prop(),
        "min_date_allowed": generate_datetime_prop(),
        "max_date_allowed": generate_datetime_prop(),
        "disabled_days": generate_datetime_prop(True),
        "initial_visible_month": generate_datetime_prop(),
    },
}
