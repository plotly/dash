import dash_table
import pandas as pd


def layout():
    df = pd.read_csv('./datasets/gapminder.csv')
    print(df.to_dict('rows'))
    return dash_table.Table(
        id='multi-header',
        columns=[{'name': i, 'id': i} for i in df.columns],
        dataframe=df.to_dict('rows')
    )
