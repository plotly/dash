import unittest
import dash_html_components


class TestDashHtmlComponents(unittest.TestCase):
    def test_imports(self):
        with open('./scripts/data/elements.txt') as f:
            elements = [
                s[0].upper() + s[1:] for s in
                f.read().split('\n')
            ]
            elements += ['MapEl', 'ObjectEl']
            for s in ['Map', 'Object']:
                elements.remove(s)

        print(dir(dash_html_components))

        self.assertEqual(
            set([d for d in dir(dash_html_components) if d[0] != '_' and d[0] == d[0].capitalize()]),
            set(elements)
        )

    def test_sample_items(self):
        Div = dash_html_components.Div
        Img = dash_html_components.Img

        layout = Div(
            Div(
                Img(src='https://plotly.com/~chris/1638.png')
            ), style={'color': 'red'}
        )

        self.assertEqual(
            repr(layout),
            ''.join([
                "Div(children=Div(Img(src='https://plotly.com/~chris/1638.png')), "
                "style={'color': 'red'})"
            ])
        )

        self.assertEqual(
            layout._namespace, 'dash_html_components'
        )
