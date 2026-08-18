from multiprocessing import Value
import flaky
import pytest
import time

from selenium.webdriver.common.keys import Keys

from dash.testing import wait

import dash
from dash import (
    Dash,
    Input,
    Output,
    State,
    MATCH,
    ALL,
    Patch,
    dcc,
    html,
    dash_table as dt,
)

from dash_test_components import MyPersistedComponent
from dash_test_components import MyPersistedComponentNested


@pytest.fixture(autouse=True)
def clear_storage(dash_duo):
    yield
    dash_duo.clear_storage()


def table_columns(names, **extra_props):
    return [
        dict(id="c{}".format(i), name=n, renamable=True, hideable=True, **extra_props)
        for i, n in enumerate(names)
    ]


def simple_table(names=("a", "b"), **props_override):
    props = dict(
        id="table",
        columns=table_columns(names),
        data=[{"c0": 0, "c1": 1}, {"c0": 2, "c1": 3}],
        persistence=True,
    )
    props.update(props_override)
    return dt.DataTable(**props)


def reloadable_app(**props_override):
    app = Dash(__name__)
    app.persistence = Value("i", 1)

    def layout():
        return html.Div(
            [
                html.Div(id="out"),
                simple_table(persistence=app.persistence.value, **props_override),
            ]
        )

    app.layout = layout

    @app.callback(
        Output("out", "children"),
        [Input("table", "columns"), Input("table", "hidden_columns")],
    )
    def report_props(columns, hidden_columns):
        return "names: [{}]; hidden: [{}]".format(
            ", ".join([col["name"] for col in columns]), ", ".join(hidden_columns or [])
        )

    return app


NEW_NAME = "mango"


def rename_and_hide(dash_duo, rename=0, new_name=NEW_NAME, hide=1):
    dash_duo.find_element(
        ".dash-header.column-{} .column-header--edit".format(rename)
    ).click()
    prompt = dash_duo.driver.switch_to.alert
    prompt.send_keys(new_name)
    prompt.accept()
    dash_duo.find_element(
        ".dash-header.column-{} .column-header--hide".format(hide)
    ).click()


def check_table_names(dash_duo, names, table_id="table"):
    dash_duo.wait_for_text_to_equal(
        "#{} .column-0 .column-header-name".format(table_id), names[0]
    )
    headers = dash_duo.find_elements("#{} .column-header-name".format(table_id))
    assert len(headers) == len(names)

    for i, n in enumerate(names):
        name_el = dash_duo.find_element(
            "#{} .column-{} .column-header-name".format(table_id, i)
        )
        assert name_el.text == n


def test_rdps001_local_reload(dash_duo):
    app = reloadable_app()
    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#out", "names: [a, b]; hidden: []")
    check_table_names(dash_duo, ["a", "b"])

    rename_and_hide(dash_duo)
    # callback output
    dash_duo.wait_for_text_to_equal(
        "#out", "names: [{}, b]; hidden: [c1]".format(NEW_NAME)
    )
    check_table_names(dash_duo, [NEW_NAME])

    dash_duo.wait_for_page()
    # callback gets persisted values, not the values provided with the layout
    dash_duo.wait_for_text_to_equal(
        "#out", "names: [{}, b]; hidden: [c1]".format(NEW_NAME)
    )
    check_table_names(dash_duo, [NEW_NAME])

    # new persistence reverts
    app.persistence.value = 2
    dash_duo.wait_for_page()
    check_table_names(dash_duo, ["a", "b"])
    rename_and_hide(dash_duo, 1, "two", 0)
    dash_duo.wait_for_text_to_equal("#out", "names: [a, two]; hidden: [c0]")
    check_table_names(dash_duo, ["two"])

    # put back the old persistence, get the old values
    app.persistence.value = 1
    dash_duo.wait_for_page()
    dash_duo.wait_for_text_to_equal(
        "#out", "names: [{}, b]; hidden: [c1]".format(NEW_NAME)
    )
    check_table_names(dash_duo, [NEW_NAME])

    # falsy persistence disables it
    app.persistence.value = 0
    dash_duo.wait_for_page()
    check_table_names(dash_duo, ["a", "b"])
    rename_and_hide(dash_duo)
    check_table_names(dash_duo, [NEW_NAME])
    dash_duo.wait_for_page()
    check_table_names(dash_duo, ["a", "b"])

    # falsy to previous truthy also brings the values
    app.persistence.value = 2
    dash_duo.wait_for_page()
    dash_duo.wait_for_text_to_equal("#out", "names: [a, two]; hidden: [c0]")
    check_table_names(dash_duo, ["two"])


def test_rdps002_session_reload(dash_duo):
    app = reloadable_app(persistence_type="session")
    dash_duo.start_server(app)
    check_table_names(dash_duo, ["a", "b"])
    rename_and_hide(dash_duo)
    check_table_names(dash_duo, [NEW_NAME])

    dash_duo.wait_for_page()
    # callback gets persisted values, not the values provided with the layout
    dash_duo.wait_for_text_to_equal(
        "#out", "names: [{}, b]; hidden: [c1]".format(NEW_NAME)
    )
    check_table_names(dash_duo, [NEW_NAME])


def test_rdps003_memory_reload(dash_duo):
    app = reloadable_app(persistence_type="memory")
    dash_duo.start_server(app)
    check_table_names(dash_duo, ["a", "b"])
    rename_and_hide(dash_duo)
    check_table_names(dash_duo, [NEW_NAME])

    dash_duo.wait_for_page()
    # no persistence after reload with persistence_type=memory
    check_table_names(dash_duo, ["a", "b"])


def test_rdps004_show_hide(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Button("Show/Hide", id="toggle-table"), html.Div(id="container")]
    )

    @app.callback(Output("container", "children"), [Input("toggle-table", "n_clicks")])
    def toggle_table(n):
        if (n or 0) % 2:
            return "nope"
        return simple_table(
            persistence_type="memory", persistence=1 if (n or 0) < 3 else 2
        )

    dash_duo.start_server(app)
    check_table_names(dash_duo, ["a", "b"])

    rename_and_hide(dash_duo)
    check_table_names(dash_duo, [NEW_NAME])

    dash_duo.find_element("#toggle-table").click()
    # table is gone
    dash_duo.wait_for_text_to_equal("#container", "nope")

    dash_duo.find_element("#toggle-table").click()
    # table is back, with persisted props
    check_table_names(dash_duo, [NEW_NAME])

    dash_duo.find_element("#toggle-table").click()
    # gone again
    dash_duo.wait_for_text_to_equal("#container", "nope")

    dash_duo.find_element("#toggle-table").click()
    # table is back, new persistence val so props not persisted
    check_table_names(dash_duo, ["a", "b"])


@flaky.flaky(max_runs=3)
def test_rdps005_persisted_props(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("toggle persisted_props", id="toggle-table"),
            html.Div(id="container"),
        ]
    )

    @app.callback(Output("container", "children"), [Input("toggle-table", "n_clicks")])
    def toggle_table(n):
        if (n or 0) % 2:
            return simple_table(persisted_props=["data", "columns.name"])
        return simple_table()

    dash_duo.start_server(app)
    check_table_names(dash_duo, ["a", "b"])

    rename_and_hide(dash_duo)
    check_table_names(dash_duo, [NEW_NAME])

    dash_duo.find_element("#toggle-table").click()
    # hidden_columns not persisted
    check_table_names(dash_duo, [NEW_NAME, "b"])

    dash_duo.find_element("#toggle-table").click()
    # back to original persisted_props hidden_columns returns
    check_table_names(dash_duo, [NEW_NAME])


def test_rdps006_move_on_page(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Button("move table", id="move-table"), html.Div(id="container")]
    )

    @app.callback(Output("container", "children"), [Input("move-table", "n_clicks")])
    def move_table(n):
        children = [html.Div("div 0", id="div0"), simple_table()]
        for i in range(1, (n or 0) + 1):
            children = [
                html.Div("div {}".format(i), id="div{}".format(i)),
                html.Div(children),
            ]
        return children

    def find_last_div(n):
        dash_duo.wait_for_text_to_equal("#div{}".format(n), "div {}".format(n))
        assert len(dash_duo.find_elements("#div{}".format(n + 1))) == 0

    dash_duo.start_server(app)
    find_last_div(0)
    check_table_names(dash_duo, ["a", "b"])

    rename_and_hide(dash_duo)
    check_table_names(dash_duo, [NEW_NAME])

    for i in range(1, 5):
        dash_duo.find_element("#move-table").click()
        find_last_div(i)
        check_table_names(dash_duo, [NEW_NAME])


def test_rdps007_one_prop_changed(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Button("hide/show cols", id="hide-cols"), html.Div(id="container")]
    )

    @app.callback(Output("container", "children"), [Input("hide-cols", "n_clicks")])
    def hide_cols(n):
        return simple_table(hidden_columns=["c0"] if (n or 0) % 2 else [])

    dash_duo.start_server(app)
    check_table_names(dash_duo, ["a", "b"])

    rename_and_hide(dash_duo)
    check_table_names(dash_duo, [NEW_NAME])

    dash_duo.find_element("#hide-cols").click()
    # hidden_columns gets the new value
    check_table_names(dash_duo, ["b"])

    dash_duo.find_element("#hide-cols").click()
    # back to original hidden_columns, but saved value won't come back
    check_table_names(dash_duo, [NEW_NAME, "b"])


def test_rdps008_unsaved_part_changed(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Button("toggle deletable", id="deletable"), html.Div(id="container")]
    )

    @app.callback(Output("container", "children"), [Input("deletable", "n_clicks")])
    def toggle_deletable(n):
        if (n or 0) % 2:
            return simple_table(columns=table_columns(("a", "b"), deletable=True))
        return simple_table()

    dash_duo.start_server(app)
    check_table_names(dash_duo, ["a", "b"])

    rename_and_hide(dash_duo)
    check_table_names(dash_duo, [NEW_NAME])
    assert len(dash_duo.find_elements(".column-header--delete")) == 0

    dash_duo.find_element("#deletable").click()
    # column names still persisted when columns.deletable changed
    # because extracted name list didn't change
    check_table_names(dash_duo, [NEW_NAME])
    assert len(dash_duo.find_elements(".column-header--delete")) == 1

    dash_duo.find_element("#deletable").click()
    check_table_names(dash_duo, [NEW_NAME])
    assert len(dash_duo.find_elements(".column-header--delete")) == 0


def test_rdps009_clear_prop_callback(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Button("reset name edits", id="reset-names"), simple_table()]
    )

    @app.callback(Output("table", "columns"), [Input("reset-names", "n_clicks")])
    def reset_names(n):
        # callbacks that return the actual persisted prop, as opposed to
        # the whole component containing them, always clear persistence, even
        # if the value is identical to the original. no_update can prevent this.
        # if we had multiple inputs, would need to check triggered
        return table_columns(("a", "b")) if n else dash.no_update

    dash_duo.start_server(app)
    check_table_names(dash_duo, ["a", "b"])

    rename_and_hide(dash_duo)
    check_table_names(dash_duo, [NEW_NAME])

    dash_duo.find_element("#reset-names").click()
    # names are reset, but not hidden_columns
    check_table_names(dash_duo, ["a"])


def test_rdps010_toggle_persistence(dash_duo):
    def make_input(persistence):
        return dcc.Input(id="persisted", value="a", persistence=persistence)

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="persistence-val", value=""),
            html.Div(make_input(""), id="persisted-container"),
            html.Div(id="out"),
        ]
    )

    @app.callback(
        Output("persisted-container", "children"), [Input("persistence-val", "value")]
    )
    def set_persistence(val):
        return make_input(val)

    @app.callback(Output("out", "children"), [Input("persisted", "value")])
    def set_out(val):
        return val

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#out", "a")
    dash_duo.find_element("#persisted").send_keys("lpaca")
    dash_duo.wait_for_text_to_equal("#out", "alpaca")

    dash_duo.find_element("#persistence-val").send_keys("s")
    dash_duo.wait_for_text_to_equal("#out", "a")
    dash_duo.find_element("#persisted").send_keys("nchovies")
    dash_duo.wait_for_text_to_equal("#out", "anchovies")

    dash_duo.find_element("#persistence-val").send_keys("2")
    dash_duo.wait_for_text_to_equal("#out", "a")
    dash_duo.find_element("#persisted").send_keys(
        Keys.BACK_SPACE
    )  # persist falsy value
    dash_duo.wait_for_text_to_equal("#out", "")

    # alpaca not saved with falsy persistence
    dash_duo.clear_input("#persistence-val")
    dash_duo.wait_for_text_to_equal("#out", "a")

    # anchovies and aardvark saved
    dash_duo.find_element("#persistence-val").send_keys("s")
    dash_duo.wait_for_text_to_equal("#out", "anchovies")
    dash_duo.find_element("#persistence-val").send_keys("2")
    dash_duo.wait_for_text_to_equal("#out", "")


def test_rdps011_toggle_persistence2(dash_duo):
    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="persistence-val", value=""),
            dcc.Input(id="persisted2", value="a", persistence=""),
            html.Div(id="out"),
        ]
    )

    # this is not a good way to set persistence, as it doesn't allow you to
    # get the right initial value. Much better is to update the whole component
    # as we do in the previous test case... but it shouldn't break this way.
    @app.callback(
        Output("persisted2", "persistence"), [Input("persistence-val", "value")]
    )
    def set_persistence(val):
        return val

    @app.callback(Output("out", "children"), [Input("persisted2", "value")])
    def set_out(val):
        return val

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#out", "a")

    dash_duo.find_element("#persistence-val").send_keys("s")
    time.sleep(0.2)
    assert not dash_duo.get_logs()
    dash_duo.wait_for_text_to_equal("#out", "a")
    dash_duo.find_element("#persisted2").send_keys("pricot")
    dash_duo.wait_for_text_to_equal("#out", "apricot")

    dash_duo.find_element("#persistence-val").send_keys("2")
    dash_duo.wait_for_text_to_equal("#out", "a")
    dash_duo.find_element("#persisted2").send_keys("rtichoke")
    dash_duo.wait_for_text_to_equal("#out", "artichoke")

    # no persistence, still goes back to original value
    dash_duo.clear_input("#persistence-val")
    dash_duo.wait_for_text_to_equal("#out", "a")

    # apricot and artichoke saved
    dash_duo.find_element("#persistence-val").send_keys("s")
    dash_duo.wait_for_text_to_equal("#out", "apricot")
    dash_duo.find_element("#persistence-val").send_keys("2")
    assert not dash_duo.get_logs()
    dash_duo.wait_for_text_to_equal("#out", "artichoke")


def test_rdps012_pattern_matching(dash_duo):
    # copy of rdps010 but with dict IDs,
    # plus a button to change the dict ID so the persistence should reset
    def make_input(persistence, n):
        return dcc.Input(
            id={"i": n, "id": "persisted"},
            className="persisted",
            value="a",
            persistence=persistence,
        )

    app = dash.Dash(__name__)
    app.layout = html.Div(
        [html.Button("click", id="btn", n_clicks=0), html.Div(id="content")]
    )

    @app.callback(Output("content", "children"), [Input("btn", "n_clicks")])
    def content(n):
        return [
            dcc.Input(
                id={"i": n, "id": "persistence-val"},
                value="",
                className="persistence-val",
            ),
            html.Div(make_input("", n), id={"i": n, "id": "persisted-container"}),
            html.Div(id={"i": n, "id": "out"}, className="out"),
        ]

    @app.callback(
        Output({"i": MATCH, "id": "persisted-container"}, "children"),
        [Input({"i": MATCH, "id": "persistence-val"}, "value")],
        [State("btn", "n_clicks")],
    )
    def set_persistence(val, n):
        return make_input(val, n)

    @app.callback(
        Output({"i": MATCH, "id": "out"}, "children"),
        [Input({"i": MATCH, "id": "persisted"}, "value")],
    )
    def set_out(val):
        return val

    dash_duo.start_server(app)

    for _ in range(3):
        dash_duo.wait_for_text_to_equal(".out", "a")
        dash_duo.find_element(".persisted input").send_keys("lpaca")
        dash_duo.wait_for_text_to_equal(".out", "alpaca")

        dash_duo.find_element(".persistence-val input").send_keys("s")
        dash_duo.wait_for_text_to_equal(".out", "a")
        dash_duo.find_element(".persisted input").send_keys("nchovies")
        dash_duo.wait_for_text_to_equal(".out", "anchovies")

        dash_duo.find_element(".persistence-val input").send_keys("2")
        dash_duo.wait_for_text_to_equal(".out", "a")
        dash_duo.find_element(".persisted input").send_keys(
            Keys.BACK_SPACE
        )  # persist falsy value
        dash_duo.wait_for_text_to_equal(".out", "")

        # alpaca not saved with falsy persistence
        dash_duo.clear_input(".persistence-val")
        dash_duo.wait_for_text_to_equal(".out", "a")

        # anchovies and aardvark saved
        dash_duo.find_element(".persistence-val input").send_keys("s")
        dash_duo.wait_for_text_to_equal(".out", "anchovies")
        dash_duo.find_element(".persistence-val input").send_keys("2")
        dash_duo.wait_for_text_to_equal(".out", "")

        dash_duo.find_element("#btn").click()


def test_rdps013_persisted_props_nested(dash_duo):
    # testing persistenceTransforms with generated test components
    # with persisted prop and persisted nested prop
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            html.Button("click me", id="btn"),
            html.Div(id="container1"),
            html.Div(id="container2"),
        ]
    )

    @app.callback(Output("container1", "children"), [Input("btn", "n_clicks")])
    def update_container(n_clicks):
        return MyPersistedComponent(id="component-propName", persistence=True)

    @app.callback(Output("container2", "children"), [Input("btn", "n_clicks")])
    def update_container2(n_clicks):
        return MyPersistedComponentNested(id="component-propPart", persistence=True)

    dash_duo.start_server(app)

    # send lower case strings to test components
    dash_duo.find_element("#component-propName").send_keys("alpaca")
    dash_duo.find_element("#component-propPart").send_keys("artichoke")
    dash_duo.find_element("#btn").click()

    # persistenceTransforms should return upper case strings
    dash_duo.wait_for_text_to_equal("#component-propName", "ALPACA")
    dash_duo.wait_for_text_to_equal("#component-propPart", "ARTICHOKE")


def test_rdps014_layout_as_list(dash_duo):
    # testing persistence with layout as list
    app = dash.Dash(__name__)
    app.layout = [
        dcc.Input(id="input-1", value="initial", persistence=True),
        html.Div(id="output-1"),
        dcc.Input(id="input-2", value="second", persistence=True),
        html.Div(id="output-2"),
    ]

    @app.callback(Output("output-1", "children"), [Input("input-1", "value")])
    def update_output_1(value):
        return f"Output 1: {value}"

    @app.callback(Output("output-2", "children"), [Input("input-2", "value")])
    def update_output_2(value):
        return f"Output 2: {value}"

    dash_duo.start_server(app)

    # Check initial values
    dash_duo.wait_for_text_to_equal("#output-1", "Output 1: initial")
    dash_duo.wait_for_text_to_equal("#output-2", "Output 2: second")

    # Change the input values
    dash_duo.clear_input("#input-1")
    dash_duo.find_element("#input-1").send_keys("changed1")
    dash_duo.clear_input("#input-2")
    dash_duo.find_element("#input-2").send_keys("changed2")

    # Verify changes
    dash_duo.wait_for_text_to_equal("#output-1", "Output 1: changed1")
    dash_duo.wait_for_text_to_equal("#output-2", "Output 2: changed2")

    # Reload the page to test persistence
    dash_duo.wait_for_page()

    # Check that persisted values are restored
    dash_duo.wait_for_text_to_equal("#output-1", "Output 1: changed1")
    dash_duo.wait_for_text_to_equal("#output-2", "Output 2: changed2")


def test_rdps015_patch_preserves_persistence(dash_duo):
    """Test carry over check in applyPersistence/persistenceMods

    When Patch() appends a new component to a list of persisted components,
    applyPersistence must not clear the localStorage entries for preexisting
    components

    The issue being checked: parsePatchProps resolves a Patch against the current Redux state,
    producing a full children array where preexisting components carry their
    current Redux values (value="edited" after user interaction). When
    applyPersistence then recurses all children, persistenceMods calls modProp
    on every component, including preexisting ones. modProp compares
    originalVal ("initial", stored in localStorage) against props.value ("edited",
    from Redux), sees a mismatch, and clears the localStorage entry

    The fix uses the patch operations record, created during application.
    persistenceMods only runs modProp on the components the patch actually
    created or wrote a prop on, and leaves the ones it carried over alone
    """

    def make_input(index):
        return html.Div(
            dcc.Input(
                id={"type": "persist-input", "index": index},
                value="initial",
                persistence=True,
                persistence_type="local",
                className="persist-input",
            )
        )

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Add", id="add-btn", n_clicks=0),
            html.Div([make_input(0), make_input(1)], id="container"),
            html.Div(id="display"),
        ]
    )

    @app.callback(
        Output("container", "children"),
        Input("add-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def add_input(n):
        p = Patch()
        p.append(make_input(n + 1))
        return p

    @app.callback(
        Output("display", "children"),
        Input({"type": "persist-input", "index": ALL}, "value"),
    )
    def show_all(values):
        return "|".join(str(v) for v in values)

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#display", "initial|initial")

    # Edit the first input so its value is persisted to localStorage as "edited"
    first_input = dash_duo.find_elements(".persist-input input")[0]
    first_input.send_keys(Keys.CONTROL + "a")
    first_input.send_keys("edited")
    dash_duo.wait_for_text_to_equal("#display", "edited|initial")

    # Add a new component via Patch, this is the operation that previously
    # caused applyPersistence to clear the localStorage entry for input 0
    dash_duo.find_element("#add-btn").click()
    dash_duo.wait_for_text_to_equal("#display", "edited|initial|initial")

    # Reload the page. The Patch was ephemeral (serverside layout only has the
    # original two inputs). If localStorage was cleared by the Patch update,
    # input 0 will revert to "initial". If the fix is working, "edited" is
    # restored from localStorage
    dash_duo.wait_for_page()
    # If localStorage was cleared by the Patch update, input 0 reverts to "initial"
    # The fix preserves the entry, so "edited" is restored from localStorage
    dash_duo.wait_for_text_to_equal("#display", "edited|initial")


def test_rdps016_patch_output_does_not_disable_persistence_of_sibling(dash_duo):
    """Confirm that patchyness is tracked per output, not per callback

    A multioutput callback can return a Patch for one output and a full
    replacement for another. Only the patched output carries preexisting
    components over from Redux (with their user edited values), so only that
    output may skip applyPersistence. The fully replaced output comes back with
    fresh server defaults, so persisted user edits must still be restored

    Before the fix, a single "this result contained a Patch" flag was attached
    to the whole callback result and applied to every output, so components in
    the replaced output were treated as preexisting and their persistence
    restore was silently skipped, the user's edit was overwritten by the
    server default
    """

    def make_patched_input(index):
        return dcc.Input(
            id={"type": "patched-input", "index": index},
            value="initial",
            persistence=True,
            persistence_type="local",
        )

    def make_replaced_input():
        return dcc.Input(
            id="replaced-input",
            value="server-default",
            persistence=True,
            persistence_type="local",
        )

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Go", id="go-btn", n_clicks=0),
            html.Div([make_patched_input(0)], id="patched-container"),
            html.Div([make_replaced_input()], id="replaced-container"),
            html.Div(id="display"),
        ]
    )

    @app.callback(
        Output("patched-container", "children"),
        Output("replaced-container", "children"),
        Input("go-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def go(n):
        p = Patch()
        p.append(make_patched_input(n))
        # Full replacement, reusing the same id: a fresh instance carrying the
        # server default, whose persisted value must be restored
        return p, [make_replaced_input()]

    @app.callback(Output("display", "children"), Input("replaced-input", "value"))
    def show(value):
        return f"replaced={value}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#display", "replaced=server-default")

    # Edit the input so "edited" is persisted to localStorage
    replaced_input = dash_duo.find_element("#replaced-input")
    replaced_input.send_keys(Keys.CONTROL + "a")
    replaced_input.send_keys("edited")
    dash_duo.wait_for_text_to_equal("#display", "replaced=edited")

    dash_duo.find_element("#go-btn").click()

    # Both outputs are applied in the same render pass, so once the patched
    # output shows two inputs (each dcc.Input renders wrapped in its own
    # container div, so they aren't adjacent siblings) the replaced output
    # has been applied too
    wait.until(lambda: len(dash_duo.find_elements("#patched-container input")) == 2, 10)

    assert (
        dash_duo.find_element("#replaced-input").get_attribute("value") == "edited"
    ), (
        "The persisted value was not restored for the fully replaced output: "
        "patchyness must be tracked per output, not per callback."
    )
    dash_duo.wait_for_text_to_equal("#display", "replaced=edited")

    assert dash_duo.get_logs() == []


def test_rdps017_patch_rebuild_same_id_restores_persistence(dash_duo):
    """Confirm that carry over detection goes by what the patch created,
    not by ids were already on the page

    A Patch that rebuilds a children list by clearing it and reappending
    components that reuse the same ids produces genuinely new component
    instances, they are not carried over from Redux, even though their
    ids were seen before the update
    """

    def make_input(value="initial"):
        return dcc.Input(
            id="rebuilt-input",
            value=value,
            persistence=True,
            persistence_type="local",
        )

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Rebuild", id="rebuild-btn", n_clicks=0),
            html.Div([make_input()], id="container"),
            html.Div(id="counter", children="0"),
            html.Div(id="display"),
        ]
    )

    @app.callback(
        Output("container", "children"),
        Output("counter", "children"),
        Input("rebuild-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def rebuild(n):
        p = Patch()
        p.clear()
        # Reuses the same id as before with the same server default value, but
        # this is a genuinely new component instance, not carried over from
        # Redux state. Persistence only restores an edit when the component's
        # current default value matches the one recorded when the edit was
        # made (see modProp), so the default must stay "initial" here
        p.append(make_input())
        # A plain, non persisted output that changes on every click, so tests
        # can wait for the rebuild to have been applied without depending on
        # the (possibly unchanged) persisted value itself
        return p, str(n)

    @app.callback(Output("display", "children"), Input("rebuilt-input", "value"))
    def show(value):
        return f"value={value}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#display", "value=initial")

    # Edit the input so "edited" is persisted to localStorage
    # Use Ctrl+A + type because .clear() doesn't work reliably
    # with react inputs
    rebuilt_input = dash_duo.find_element("#rebuilt-input")
    rebuilt_input.send_keys(Keys.CONTROL + "a")
    rebuilt_input.send_keys("edited")
    dash_duo.wait_for_text_to_equal("#display", "value=edited")

    dash_duo.find_element("#rebuild-btn").click()

    # Wait for the rebuild to be applied (the counter changes regardless of
    # what value the rebuilt input ends up with), then check whether
    # persistence restored the user's edit on top of the rebuilt component
    dash_duo.wait_for_text_to_equal("#counter", "1")

    assert dash_duo.find_element("#rebuilt-input").get_attribute("value") == "edited", (
        "The persisted value was not restored for a component rebuilt with a "
        "reused id: a component the patch inserted is a new instance, whatever "
        "id it reuses, so persistence must run on it."
    )
    dash_duo.wait_for_text_to_equal("#display", "value=edited")

    assert dash_duo.get_logs() == []
