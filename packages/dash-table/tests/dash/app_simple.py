import dash_table
import pandas as pd


def layout():
    df = pd.read_csv("./datasets/gapminder.csv")
    return dash_table.Table(
        id=__name__,
        columns=[{"name": i, "id": i} for i in df.columns],
        dataframe=df.to_dict("rows"),
    )
