from dash import html, Dash, Output, Input, callback, dcc, ALL, State


def create_dropdown_option(name):
    return {
        "value": f"value_{name}",
        "label": dcc.Markdown(f"label_{name}"),
        "title": f"title_{name}",
    }


def get_dropdown_options(num_of_options):
    return [create_dropdown_option(name) for name in range(num_of_options)]


def test_capr001_dynamic_dropdown_component_labels(dash_duo):
    # Regression test for the community bug where dynamically regenerating
    # dropdowns whose option labels are components (components as props),
    # with persistence on, while appending a new option, crashed with
    # "can't access property 'props', layout is undefined".
    #
    # The label components are rendered out-of-tree via `ExternalWrapper`.
    # When the hosting subtree is replaced by a callback while the wrapper
    # reconciles in place (rather than remounting), its layout entry was
    # wiped but it still tried to update props at the stale path. The
    # wrapper now re-inserts itself, and `updateProps` no-ops on a missing
    # path instead of crashing.
    app = Dash(__name__)

    app.layout = html.Div(
        id="top-level-component",
        children=[
            dcc.Dropdown(
                ["option_set_1", "option_set_2"],
                "option_set_1",
                id="dropdown_selector",
                persistence=True,
                persistence_type="local",
            ),
            html.Div(id="dropdowns_container", children=[]),
        ],
    )

    @callback(
        Output("dropdowns_container", "children"),
        Input("dropdown_selector", "value"),
        State({"aio_id": "extensible_dropdown", "index": ALL}, "options"),
    )
    def swap_dropdowns(dropdown_selector_value, prev_options):
        number_of_dds = 2 if dropdown_selector_value == "option_set_1" else 4
        if prev_options:
            options = prev_options[0]
        else:
            options = get_dropdown_options(3)

        options.append(create_dropdown_option(len(options)))

        dropdowns_to_output = []
        for i in range(number_of_dds):
            dropdowns_to_output.append(
                html.Div(
                    [
                        html.Div(f"Input: {i}"),
                        dcc.Dropdown(
                            options=options,
                            id={"aio_id": "extensible_dropdown", "index": f"{i}"},
                            persistence=True,
                            persistence_type="local",
                        ),
                    ]
                )
            )
        return dropdowns_to_output

    dash_duo.start_server(app)

    # Two extensible dropdowns render on load.
    dash_duo._wait_for(
        lambda _: len(dash_duo.find_elements("#dropdowns_container .dash-dropdown"))
        == 2,
        timeout=5,
        msg="expected 2 extensible dropdowns on load",
    )

    # Open the first extensible dropdown and select its first option: this
    # mounts the option's component label into the value display.
    dash_duo.find_elements("#dropdowns_container .dash-dropdown")[0].click()
    dash_duo.wait_for_element(".dash-dropdown-option")
    dash_duo.find_elements(".dash-dropdown-option")[0].click()
    dash_duo.wait_for_text_to_equal(
        "#dropdowns_container .dash-dropdown-value", "label_0"
    )

    # Swap to option_set_2: regenerates all dropdowns and appends a new
    # option. This used to crash and leave the container unchanged.
    dash_duo.find_element("#dropdown_selector").click()
    dash_duo.wait_for_element("#dropdown_selector ~ * .dash-dropdown-option")
    for opt in dash_duo.find_elements(".dash-dropdown-option"):
        if "option_set_2" in opt.text:
            opt.click()
            break

    # Four extensible dropdowns now render...
    dash_duo._wait_for(
        lambda _: len(dash_duo.find_elements("#dropdowns_container .dash-dropdown"))
        == 4,
        timeout=5,
        msg="expected 4 extensible dropdowns after swap",
    )
    # ...the persisted selection's component label still displays...
    dash_duo.wait_for_text_to_equal(
        "#dropdowns_container .dash-dropdown-value", "label_0"
    )

    # ...and the appended option's component label renders when opened.
    dash_duo.find_elements("#dropdowns_container .dash-dropdown")[0].click()
    dash_duo._wait_for(
        lambda _: [e.text for e in dash_duo.find_elements(".dash-dropdown-option")]
        == ["label_0", "label_1", "label_2", "label_3", "label_4"],
        timeout=5,
        msg="appended component label should render after swap",
    )

    assert dash_duo.get_logs() == [], "browser console errors after swap"
