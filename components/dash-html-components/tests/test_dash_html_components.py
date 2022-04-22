import pytest
import dash
from dash import html


def test_imports():
    with open("./scripts/data/elements.txt") as f:
        elements = [s[0].upper() + s[1:] for s in f.read().split("\n")]
        elements += ["MapEl", "ObjectEl"]
        for s in ["Map", "Object"]:
            elements.remove(s)

    dir_set = set(
        [
            d
            for d in dir(dash.html)
            if d[0] != "_" and d[0] != "@" and d[0] == d[0].capitalize()
        ]
    )
    assert dir_set == set(elements)


def test_sample_items():
    layout = html.Div(
        html.Div(html.Img(src="https://plotly.com/~chris/1638.png")),
        style={"color": "red"},
    )

    expected = (
        "Div(children=Div(Img(src='https://plotly.com/~chris/1638.png')), "
        "style={'color': 'red'})"
    )
    assert repr(layout) == expected

    assert layout._namespace == "dash_html_components"


def test_objectEl():
    layout = html.ObjectEl(data="something", **{"data-x": "else"})
    assert repr(layout) == "ObjectEl(data='something', data-x='else')"

    with pytest.raises(TypeError):
        html.ObjectEl(datax="something")


def test_customDocs():
    assert "CAUTION" in html.Script.__doc__[:100]
    assert "OBSOLETE" in html.Blink.__doc__[:100]
    assert "DEPRECATED" in html.Marquee.__doc__[:100]
