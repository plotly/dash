import pandas as pd


class Dash():
    def __init__(self):
        self.df = pd.read_csv('http://www.stat.ubc.ca/~jenny/notOcto/STAT545A/'
                              'examples/gapminder/data/'
                              'gapminderDataFiveYear.txt', sep='\t')
        self.country = 'United States'
        self.yaxis = 'pop'

    def on_page_load(self):
        pass

    def on_pong(self, message):
        print('on_pong')
        messages = []
        messages.extend(self.replot(message))
        return messages

    def replot(self, app_state):
        self.xaxis = app_state['xaxis']
        self.yaxis = app_state['yaxis']
        self.size = app_state['size']

        labels = {
            'pop': 'Population',
            'lifeExp': 'Life Expectancy',
            'gdpPercap': 'GDP per Capita'
        }

        dfi = self.df[(self.df['year'] == int(app_state['slider'])) &
                      (self.df['country'] != 'Kuwait')]

        traces = []

        for c in dfi['continent'].unique():
            dfc = dfi[dfi['continent'] == c]
            traces.append({
                'x': dfc[self.xaxis],
                'y': dfc[self.yaxis],
                'text': dfc['country'],
                'mode': 'markers',
                'marker': {
                    'size': dfc[self.size],
                    'sizeref': max(self.df[self.size])/7500,
                    'sizemode': 'area'
                },
                'name': c
            })

        fig = {
            'data': traces,
            'layout': {
                'xaxis': {
                    'title': labels[self.xaxis],
                    'type': 'log'
                },
                'yaxis': {
                    'title': labels[self.yaxis],
                },
                'hovermode': 'closest',
                'annotations': [
                    {
                        'text': str(app_state['slider']),
                        'showarrow': False,
                        'x':0,
                        'y':1,
                        'font':{
                            'size': 24,
                            'color': "rgb(102, 102, 102)"
                        },
                        'xref': "paper",
                        'yref': "paper"
                    }
                ]
            }
        }

        messages = [
            {
                'id': 'bubbles',
                'task': 'newPlot',
                'data': fig['data'],
                'layout': fig['layout']
            }
        ]

        if 'click' in app_state:
            curveNumber = app_state['click']['points'][0]['curveNumber']
            pointNumber = app_state['click']['points'][0]['pointNumber']
            text = messages[0]['data'][curveNumber]['text']
            self.country = text.get_value(text.index[pointNumber])

        dfi = self.df[self.df['country'] == self.country]

        fig = {
            'data': [
                {
                    'x': pd.to_datetime(dfi['year'], format='%Y'),
                    'y': dfi[self.yaxis]
                }
            ],
            'layout': {
                'yaxis': {
                    'title': labels[self.yaxis]
                },
                # 'title': self.country,
                'annotations': [
                    {
                        'text': self.country,
                        'showarrow': False,
                        'x': 0,
                        'y': 1,
                        'font': {
                            'size': 24,
                            'color': "rgb(102, 102, 102)"
                        },
                        'xref': "paper",
                        'yref': "paper"
                    }
                ]
            }
        }

        messages.extend([
            {
                'id': 'line-chart',
                'task': 'newPlot',
                'data': fig['data'],
                'layout': fig['layout']
            }
        ])

        return messages
