import dash_table
import pandas as pd


def layout():
    df = pd.read_csv("datasets/gapminder.csv")
    return dash_table.Table(
        id=__name__,
        columns=[
            {"name": ["Year", ""], "id": "year"},
            {"name": ["City", "Montreal"], "id": "montreal"},
            {"name": ["City", "Toronto"], "id": "toronto"},
            {"name": ["City", "Ottawa"], "id": "ottawa", "hidden": True},
            {"name": ["City", "Vancouver"], "id": "vancouver"},
            {"name": ["Climate", "Temperature"], "id": "temp"},
            {"name": ["Climate", "Humidity"], "id": "humidity"},
        ],
        data=[
            {
                "year": i,
                "montreal": i * 10,
                "toronto": i * 100,
                "ottawa": i * -1,
                "vancouver": i * -10,
                "temp": i * -100,
                "humidity": i * 0.1,
            }
            for i in range(100)
        ],
        merge_duplicate_headers=True,
    )
