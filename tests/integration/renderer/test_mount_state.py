from dash import Dash, html

import dash_test_components as dt


def test_mnst001_mount_setprops_survives_first_render(dash_duo):
    # Regression test for #3929: a component that establishes its own initial
    # state on mount via setProps (the pattern dbc Tabs uses to select its
    # default active_tab) had that update wiped on the very first render,
    # because the parent's fresh render reset all descendant layout hashes
    # before the mount-time update took effect. The component is rendered as
    # a child (a children-prop, which is flagged as a fresh render on first
    # mount), so it exercises that reset path.
    app = Dash(__name__)
    app.layout = html.Div(dt.MountStateComponent(id="m"))

    dash_duo.start_server(app)

    # "mounted" is set by the component's mount effect; "initial" is the
    # default that remains if the update was wiped.
    dash_duo.wait_for_text_to_equal("#m", "mounted", timeout=6)
    assert dash_duo.get_logs() == []


def test_mnst002_mount_setprops_survives_when_nested(dash_duo):
    # Same as above but nested deeper, so the reset originates from an
    # ancestor rather than the direct parent.
    app = Dash(__name__)
    app.layout = html.Div(html.Div(dt.MountStateComponent(id="m")))

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#m", "mounted", timeout=6)
    assert dash_duo.get_logs() == []
