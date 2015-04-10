import pandas as pd
import numpy as np


class Graph():
    def __init__(self):
        self.df = pd.read_csv('http://www.stat.ubc.ca/~jenny/notOcto/STAT545A/'
                              'examples/gapminder/data/'
                              'gapminderDataFiveYear.txt', sep='\t')
        self.country = 'United States'
        self.yaxis = 'pop'

    def on_page_load(self):
        pass

    def on_pong(self):
        print('on_pong')
        messages = []

        messages.extend(self.replot({'slider': 1952}))
        messages.extend(self.replot({'select': True, 'yaxis': self.yaxis}))
        return messages

    def replot(self, app_state):
        if 'click' in app_state or 'select' in app_state:
            return self.on_click(app_state)
        else:
            return self.on_slide(app_state)

    def on_slide(self, app_state):
        dfi = self.df[(self.df['year'] == app_state['slider']) &
                      (self.df['country'] != 'Kuwait')]
        traces = []
        for c in dfi['continent'].unique():
            dfc = dfi[dfi['continent'] == c]
            traces.append({
                'x': dfc['gdpPercap'],
                'y': dfc['lifeExp'],
                'text': dfc['country'],
                'mode': 'markers',
                'marker': {
                    'size': dfc['pop'],
                    'sizeref': max(self.df['pop'])/7500,
                    'sizemode': 'area'
                },
                'name': c
            })

        fig = {
            'data': traces,
            'layout': {
                'xaxis': {
                    'title': 'GDP per Capita',
                    'type': 'log',
                    'autorange': False,
                    'range': np.log10([(
                        min(self.df['gdpPercap'])*0.5),
                        max(self.df['gdpPercap'])*1.1])
                },
                'yaxis': {
                    'title': 'Life Expectancy',
                    'autorange': False,
                    'range': [
                        min(self.df['lifeExp'])*0.8,
                        max(self.df['lifeExp'])*1.2]
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

        return messages

    def on_click(self, app_state):
        if 'click' in app_state:
            curveNumber = app_state['click']['points'][0]['curveNumber']
            pointNumber = app_state['click']['points'][0]['pointNumber']
            text = self.on_slide(app_state)[0]['data'][curveNumber]['text']
            self.country = text.get_value(text.index[pointNumber])
        else:
            self.yaxis = app_state['yaxis']

        dfi = self.df[self.df['country'] == self.country]
        labels = {
            'pop': 'Population',
            'lifeExp': 'Life Expectancy',
            'gdpPercap': 'GDP per Capita'
        }
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
        messages = [
            {
                'id': 'line',
                'task': 'newPlot',
                'data': fig['data'],
                'layout': fig['layout']
            }
        ]

        return messages
