import dash_table
import pandas as pd

sanitized_name = __name__.replace(".", "-")

def layout():
    df = pd.read_csv("./datasets/gapminder.csv")
    return dash_table.DataTable(
        id=sanitized_name,
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("rows"),
    )
