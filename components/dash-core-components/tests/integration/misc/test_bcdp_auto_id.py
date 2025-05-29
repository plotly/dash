from dash import Dash, Input, Output, dcc, html


def test_msai001_auto_id_assert(dash_dcc):
    app = Dash(__name__)

    input1 = dcc.Input(value="Hello Input 1")
    input2 = dcc.Input(value="Hello Input 2")
    input3 = dcc.Input(value=3)
    output1 = html.Div()
    output2 = html.Div()
    output3 = html.Div(id="output-3")
    slider = dcc.Slider(0, 10, value=9)

    app.layout = html.Div([input1, input2, output1, output2, output3, input3, slider])

    @app.callback(Output(output1, "children"), Input(input1, "value"))
    def update(v):
        return f"Output1: Input1={v}"

    @app.callback(Output(output2, "children"), Input(input2, "value"))
    def update(v):
        return f"Output2: Input2={v}"

    @app.callback(
        Output("output-3", "children"), Input(input1, "value"), Input(input2, "value")
    )
    def update(v1, v2):
        return f"Output3: Input1={v1}, Input2={v2}"

    @app.callback(Output(slider, "value"), Input(input3, "value"))
    def update(v):
        return v

    # Verify the auto-generated IDs are stable
    assert output1.id == "e3e70682-c209-4cac-629f-6fbed82c07cd"
    assert input1.id == "82e2e662-f728-b4fa-4248-5e3a0a5d2f34"
    assert output2.id == "d4713d60-c8a7-0639-eb11-67b367a9c378"
    assert input2.id == "23a7711a-8133-2876-37eb-dcd9e87a1613"
    # we make sure that the if the id is set explicitly, then it is not replaced by random id
    assert output3.id == "output-3"

    dash_dcc.start_server(app)

    def escape_id(dep):
        _id = dep.id
        if _id[0] in "0123456789":
            _id = "\\3" + _id[0] + " " + _id[1:]
        return "#" + _id

    dash_dcc.wait_for_element(".rc-slider")
    dash_dcc.find_element(escape_id(input1))
    dash_dcc.find_element(escape_id(input2))
    dash_dcc.wait_for_text_to_equal(escape_id(output1), "Output1: Input1=Hello Input 1")
    dash_dcc.wait_for_text_to_equal(escape_id(output2), "Output2: Input2=Hello Input 2")
    dash_dcc.wait_for_text_to_equal(
        escape_id(output3), "Output3: Input1=Hello Input 1, Input2=Hello Input 2"
    )
