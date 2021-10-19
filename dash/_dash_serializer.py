import base64
import json
from typing import cast

# from os import remove
import random
import io
import tempfile
import pandas as pd
from pandas.core.frame import DataFrame
import pyarrow as pa

srd = random.Random(0)


PROP_TYPE = "__type"
PROP_VALUE = "__value"
PROP_ENGINE = "__engine"

NotSerializable = Exception("NotSerializable")


class DataFrameSerializer:
    @classmethod
    def __serialize_using_fastparquet(cls, df):
        outputPath = tempfile.NamedTemporaryFile("w").name
        df.to_parquet(
            outputPath, compression="gzip", engine="fastparquet"
        )  # TODO: check https://pandas.pydata.org/pandas-docs/dev/reference/api/pandas.DataFrame.to_parquet.html
        with open(outputPath, "rb") as f:
            buffer_val = f.read()
            f.close()
            # remove(outputPath)
        return base64.b64encode(buffer_val).decode("utf-8")

    @classmethod
    def pyarrow_table_to_bytes(cls, table: pa.Table) -> bytes:
        sink = pa.BufferOutputStream()
        writer = pa.RecordBatchStreamWriter(sink, table.schema)
        writer.write_table(table)
        writer.close()
        byteData = cast(bytes, sink.getvalue().to_pybytes())
        return base64.b64encode(byteData).decode("utf-8")

    @classmethod
    def __serialize_using_pyarrow(cls, df, useFile=False, useParquetFormat=False):
        if not useParquetFormat:
            table = pa.Table.from_pandas(df)
            return DataFrameSerializer.pyarrow_table_to_bytes(table)
        elif useFile:
            outputPath = tempfile.NamedTemporaryFile("w")
            df.to_parquet(outputPath, compression="gzip", engine="pyarrow")
            with open(outputPath, "rb") as f:
                buffer_val = f.read()
                f.close()
                # remove(outputPath)
            return base64.b64encode(buffer_val).decode("utf-8")
        else:
            ret_buffer = df.to_parquet(compression="gzip", engine="pyarrow")
            return base64.b64encode(ret_buffer).decode("utf-8")

    @classmethod
    def serialize(cls, prop, engine="fastparquet"):
        if engine == "fastparquet":
            serialized_value = DataFrameSerializer.__serialize_using_fastparquet(prop)
        elif engine == "pyarrow":
            serialized_value = DataFrameSerializer.__serialize_using_pyarrow(prop)
        else:
            serialized_value = {
                "records": prop.to_dict("records"),
                "columns": prop.columns,
            }
        return {
            PROP_TYPE: "pd.DataFrame",
            PROP_VALUE: serialized_value,
            PROP_ENGINE: engine,
        }

    @classmethod
    def deserialize(cls, prop):
        # TODO: Consider partial updates? - use _id to find from file for original/full DataFrame, then apply patch only?
        [engine, value] = [
            prop[PROP_ENGINE],
            prop[PROP_VALUE],
        ]
        if engine == "to_dict":
            return DataFrame.from_records(value)
        else:
            return pd.read_parquet(io.BytesIO(value), engine)


class DashSerializer:
    @classmethod
    def __serialize_value(cls, prop):
        serializeFn = getattr(prop, "serialize", None)
        if serializeFn:
            return serializeFn()

        if isinstance(prop, pd.DataFrame):
            # return serializer.serialize(prop, engine="pyarrow")
            return DataFrameSerializer.serialize(prop, engine="to_dict")
        return NotSerializable

    @classmethod
    def __deserialize_value(cls, prop):
        deserializeFn = getattr(prop, "deserialize", None)
        if deserializeFn:
            return deserializeFn()

        jsonObj = json.loads(prop) if isinstance(prop, str) else prop
        _type = (
            jsonObj[PROP_TYPE]
            if isinstance(jsonObj, dict) and PROP_TYPE in jsonObj
            else None
        )
        if _type == "pd.DataFrame":
            return DataFrameSerializer.deserialize(jsonObj)
        return prop

    @classmethod
    def deserialize(cls, obj):
        props = obj if isinstance(obj, list) else [obj]
        return [
            (
                {**prop, "value": DashSerializer.__deserialize_value(prop["value"])}
                if "value" in prop
                else prop
            )
            for prop in props
        ]

    @classmethod
    def serialize(cls, obj):
        result = DashSerializer.__serialize_value(obj)
        if result == NotSerializable:
            return result

        # Plotly
        try:
            obj = obj.to_plotly_json()
        except AttributeError:
            pass

        if isinstance(obj, (list, tuple)):
            if obj:
                # Must process list recursively even though it may be slow
                return [cls.serialize(v) for v in obj]

        # Recurse into lists and dictionaries
        if isinstance(obj, dict):
            return {k: cls.serialize(v) for k, v in obj.items()}

        return obj
