from dash import Dash, dcc, html


def test_mdcap001_dcc_components_as_props(dash_dcc):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Checklist(
                [
                    {"label": html.H2("H2 label"), "value": "h2"},
                    {"label": html.A("Link in checklist", href="#"), "value": "a"},
                ],
                id="checklist",
            ),
            dcc.RadioItems(
                [
                    {"label": html.H3("on"), "value": "on"},
                    {"label": html.P("off"), "value": "off"},
                ],
                id="radio-items",
            ),
            dcc.Dropdown(
                [
                    {"label": html.H4("h4"), "value": "h4"},
                    {"label": html.H6("h6"), "value": "h6"},
                ],
                id="dropdown",
            ),
            dcc.Dropdown(
                [
                    {"label": "one", "value": 1, "search": "uno"},
                    {"label": "two", "value": 2, "search": "dos"},
                ],
                id="indexed-search",
            ),
        ]
    )

    dash_dcc.start_server(app)

    dash_dcc.wait_for_text_to_equal("#checklist h2", "H2 label")
    dash_dcc.wait_for_text_to_equal("#checklist a", "Link in checklist")

    dash_dcc.wait_for_text_to_equal("#radio-items h3", "on")
    dash_dcc.wait_for_text_to_equal("#radio-items p", "off")

    dash_dcc.find_element("#dropdown").click()
    dash_dcc.wait_for_text_to_equal("#dropdown h4", "h4")
    dash_dcc.wait_for_text_to_equal("#dropdown h6", "h6")

    search_input = dash_dcc.find_element("#dropdown input")
    search_input.send_keys("4")
    options = dash_dcc.find_elements("#dropdown .VirtualizedSelectOption")

    assert len(options) == 1
    assert options[0].text == "h4"

    def search_indexed(value, length, texts):
        search = dash_dcc.find_element("#indexed-search input")
        dash_dcc.clear_input(search)
        search.send_keys(value)
        opts = dash_dcc.find_elements("#indexed-search .VirtualizedSelectOption")

        assert len(opts) == length
        assert [o.text for o in opts] == texts

    search_indexed("o", 2, ["one", "two"])
    search_indexed("1", 1, ["one"])
    search_indexed("uno", 1, ["one"])
    # FIXME clear_input doesnt work well when the input is focused. (miss the o)
    dash_dcc.clear_input("#indexed-search input")
    search_indexed("dos", 1, ["two"])
