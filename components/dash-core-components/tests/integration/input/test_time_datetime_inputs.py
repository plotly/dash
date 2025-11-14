"""
Tests for time and datetime-local input types in dcc.Input component.

This module tests the newly added support for 'time' and 'datetime-local'
input types that were previously unsupported in dcc.Input.
"""

from dash import Dash, Input, Output, dcc, html


def test_time_input_functionality(dash_dcc):
    """Test that time input type works correctly."""
    app = Dash(__name__)
    app.layout = html.Div([
        dcc.Input(
            id='time-input',
            type='time',
            step=1,
            value='14:30:15'
        ),
        html.Div(id='time-output')
    ])

    @app.callback(
        Output('time-output', 'children'),
        Input('time-input', 'value')
    )
    def update_time_output(time_value):
        return f"Time: {time_value}"

    dash_dcc.start_server(app)

    # Check that the input has the correct type
    time_input = dash_dcc.find_element('#time-input')
    assert time_input.get_attribute('type') == 'time'
    assert time_input.get_attribute('value') == '14:30:15'

    # Test updating the time value
    time_input.clear()
    time_input.send_keys('09:45:30')

    # Wait for callback to update
    dash_dcc.wait_for_text_to_equal('#time-output', 'Time: 09:45:30')

    assert dash_dcc.get_logs() == []


def test_datetime_local_input_functionality(dash_dcc):
    """Test that datetime-local input type works correctly."""
    app = Dash(__name__)
    app.layout = html.Div([
        dcc.Input(
            id='datetime-input',
            type='datetime-local',
            step=1,
            value='2023-12-25T18:30:00'
        ),
        html.Div(id='datetime-output')
    ])

    @app.callback(
        Output('datetime-output', 'children'),
        Input('datetime-input', 'value')
    )
    def update_datetime_output(datetime_value):
        return f"DateTime: {datetime_value}"

    dash_dcc.start_server(app)

    # Check that the input has the correct type
    datetime_input = dash_dcc.find_element('#datetime-input')
    assert datetime_input.get_attribute('type') == 'datetime-local'
    assert datetime_input.get_attribute('value') == '2023-12-25T18:30:00'

    # Test updating the datetime value
    datetime_input.clear()
    datetime_input.send_keys('2024-01-01T12:00:00')

    # Wait for callback to update
    dash_dcc.wait_for_text_to_equal('#datetime-output', 'DateTime: 2024-01-01T12:00:00')

    assert dash_dcc.get_logs() == []


def test_time_input_with_debounce(dash_dcc):
    """Test that time input works correctly with debounce."""
    app = Dash(__name__)
    app.layout = html.Div([
        dcc.Input(
            id='time-debounce-input',
            type='time',
            debounce=True,
            value='12:00:00'
        ),
        html.Div(id='time-debounce-output')
    ])

    @app.callback(
        Output('time-debounce-output', 'children'),
        Input('time-debounce-input', 'value')
    )
    def update_debounce_output(time_value):
        return f"Time with debounce: {time_value}"

    dash_dcc.start_server(app)

    time_input = dash_dcc.find_element('#time-debounce-input')
    assert time_input.get_attribute('type') == 'time'

    # With debounce=True, value should update only after losing focus or Enter key
    time_input.clear()
    time_input.send_keys('15:30:45')

    # Trigger blur event to commit the debounced value
    dash_dcc.find_element('body').click()  # Click somewhere else to blur

    dash_dcc.wait_for_text_to_equal('#time-debounce-output', 'Time with debounce: 15:30:45')

    assert dash_dcc.get_logs() == []


def test_datetime_local_input_with_min_max(dash_dcc):
    """Test that datetime-local input works with min and max attributes."""
    app = Dash(__name__)
    app.layout = html.Div([
        dcc.Input(
            id='datetime-minmax-input',
            type='datetime-local',
            min='2023-01-01T00:00:00',
            max='2023-12-31T23:59:59',
            value='2023-06-15T12:00:00'
        ),
        html.Div(id='datetime-minmax-output')
    ])

    @app.callback(
        Output('datetime-minmax-output', 'children'),
        Input('datetime-minmax-input', 'value')
    )
    def update_minmax_output(datetime_value):
        return f"DateTime with constraints: {datetime_value}"

    dash_dcc.start_server(app)

    datetime_input = dash_dcc.find_element('#datetime-minmax-input')
    assert datetime_input.get_attribute('type') == 'datetime-local'
    assert datetime_input.get_attribute('min') == '2023-01-01T00:00:00'
    assert datetime_input.get_attribute('max') == '2023-12-31T23:59:59'
    assert datetime_input.get_attribute('value') == '2023-06-15T12:00:00'

    assert dash_dcc.get_logs() == []
