import dash_table
import pandas as pd

# Subset of https://www.irs.gov/pub/irs-soi/16zpallagi.csv
df = pd.read_csv("./datasets/16zpallagi-25cols-100klines.csv")
data = df.to_dict("rows")

def layout():
    return dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns],
        data=data,
        pagination_mode=False,
        virtualization=True,
        editable=True,
        n_fixed_rows=1,
        style_table={
            "height": 800,
            "max_height": 800,
            "width": 1300,
            "max_width": 1300
        },
        style_data={
            "width": 50,
            "max_width": 50,
            "min_width": 50
        }
    )
