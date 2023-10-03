from dash import Dash, html, dcc, callback, Output, Input

import dash.testing.wait as wait
import time


from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


def test_clp001_clipboard_text(dash_dcc_headed):
    copy_text = "Hello, Dash!"
    app = Dash(__name__, prevent_initial_callbacks=True)
    app.layout = html.Div(
        [
            html.Div(copy_text, id="copy"),
            dcc.Clipboard(id="copy_icon", target_id="copy"),
            dcc.Textarea(id="paste"),
        ]
    )
    dash_dcc_headed.start_server(app)

    dash_dcc_headed.find_element("#copy_icon").click()
    #  time.sleep(2)
    dash_dcc_headed.find_element("#paste").click()
    ActionChains(dash_dcc_headed.driver).key_down(Keys.CONTROL).send_keys("v").key_up(
        Keys.CONTROL
    ).perform()

    wait.until(
        lambda: dash_dcc_headed.find_element("#paste").get_attribute("value")
        == copy_text,
        timeout=3,
    )


def test_clp002_clipboard_text(dash_dcc_headed):
    copy_text = "Copy this text to the clipboard"
    app = Dash(__name__, prevent_initial_callbacks=True)
    app.layout = html.Div(
        [dcc.Clipboard(id="copy_icon", content=copy_text), dcc.Textarea(id="paste")]
    )
    dash_dcc_headed.start_server(app)

    dash_dcc_headed.find_element("#copy_icon").click()
    time.sleep(1)
    dash_dcc_headed.find_element("#paste").click()
    ActionChains(dash_dcc_headed.driver).key_down(Keys.CONTROL).send_keys("v").key_up(
        Keys.CONTROL
    ).perform()

    wait.until(
        lambda: dash_dcc_headed.find_element("#paste").get_attribute("value")
        == copy_text,
        timeout=3,
    )

def test_clp003_clipboard_text(dash_dcc_headed):
    copy_text = "Copy this text to the clipboard using a separate button"
    app = Dash(__name__, prevent_initial_callbacks=True)
    app.layout = html.Div(
        [dcc.Clipboard(id="copy_icon", content=copy_text), dcc.Textarea(id="paste"), html.Button("Copy", id="copy_button")]
    )
    @callback(
        Output("copy_icon", "content"),
        Input("copy_button", "n_clicks"),
        prevent_initial_call=True,
    )
    def selected(clicks):
        return f"{clicks}"
    
    dash_dcc_headed.start_server(app)

    dash_dcc_headed.find_element("#copy_button").click()
    time.sleep(1)
    dash_dcc_headed.find_element("#paste").click()
    ActionChains(dash_dcc_headed.driver).key_down(Keys.CONTROL).send_keys("v").key_up(
        Keys.CONTROL
    ).perform()

    wait.until(
        lambda: dash_dcc_headed.find_element("#paste").get_attribute("value")
        == copy_text,
        timeout=3,
    )
