from dash import Dash, dcc, html


def test_slsl_extreme_range_marks_density(dash_dcc):
    """
    Test that extreme ranges don't generate too many overlapping marks.

    With min=-1, max=480256671, and container width ~365px, we should have
    no more than ~7 marks to prevent overlap (given the long labels).
    """
    app = Dash(__name__)
    app.layout = html.Div(
        style={"width": "365px"},
        children=[
            dcc.RangeSlider(
                id="rangeslider-extreme",
                min=-1,
                max=480256671,
                value=[-1, 480256671],
            )
        ],
    )

    dash_dcc.start_server(app)
    # Wait for component to render
    dash_dcc.wait_for_element("#rangeslider-extreme")

    # Count the rendered marks
    marks = dash_dcc.find_elements(".dash-slider-mark")
    mark_count = len(marks)

    # Get the actual mark text to verify what's rendered
    mark_texts = [mark.text for mark in marks]

    # Should have between 2 and 7 marks (min/max plus a few intermediate)
    assert 2 <= mark_count <= 7, (
        f"Expected 2-7 marks for extreme range, but found {mark_count}. "
        f"This suggests overlapping marks. Labels: {mark_texts}"
    )

    # Verify min and max are included
    assert "-1" in mark_texts, "Min value (-1) should be included in marks"
    assert any(
        "480" in text or "M" in text for text in mark_texts
    ), "Max value should be included in marks"

    assert dash_dcc.get_logs() == []


def test_slsl_extreme_range_no_width(dash_dcc):
    """
    Test that extreme ranges work even before width is measured.

    This simulates the initial render state where sliderWidth is null.
    """
    app = Dash(__name__)
    app.layout = html.Div(
        # No explicit width, so ResizeObserver will measure it
        children=[
            dcc.RangeSlider(
                id="rangeslider-no-width",
                min=-1,
                max=480256671,
                value=[-1, 480256671],
            )
        ],
    )

    dash_dcc.start_server(app)

    # Wait for component to render
    dash_dcc.wait_for_element("#rangeslider-no-width")

    # Count the rendered marks
    marks = dash_dcc.find_elements(".dash-slider-mark")
    mark_count = len(marks)

    assert mark_count <= 11, f"Expected default 11 marks, but found {mark_count}"

    assert dash_dcc.get_logs() == []
