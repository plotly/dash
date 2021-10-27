from dash import _dash_serializer
import base64
import io


def test_data_frame_serializer_fastparquet():
    import pandas as pd
    import numpy as np

    df = pd.DataFrame({"x": np.array([1, 2, 3, 4]), "y": np.array([5, 4, 3, 2])})
    serialized_df = _dash_serializer.DataFrameSerializer._DataFrameSerializer__serialize_using_fastparquet(
        df
    )
    df_parquet = base64.b64decode(serialized_df.encode("utf-8"))
    df2 = pd.read_parquet(io.BytesIO(df_parquet))
    assert all(df == df2)
