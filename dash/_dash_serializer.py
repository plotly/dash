import base64
import json
from typing import cast

from os import remove
import io
import tempfile
import pandas as pd
from pandas.core.frame import DataFrame
import pyarrow as pa

PROP_TYPE = "__type"
PROP_VALUE = "__value"
PROP_ENGINE = "__engine"


class DataFrameSerializer:
    @classmethod
    def __serialize_using_fastparquet(cls, df):
        with tempfile.NamedTemporaryFile("w") as temp_file:
            outputPath = temp_file.name

        df.to_parquet(outputPath, compression="gzip", engine="fastparquet")
        with open(outputPath, "rb") as f:
            buffer_val = f.read()
            f.close()
            remove(outputPath)
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

        if useFile:
            with tempfile.NamedTemporaryFile("w") as temp_file:
                outputPath = temp_file.name

            df.to_parquet(outputPath, compression="gzip", engine="pyarrow")
            with open(outputPath, "rb") as f:
                buffer_val = f.read()
                f.close()
                remove(outputPath)
            return base64.b64encode(buffer_val).decode("utf-8")

        ret_buffer = df.to_parquet(compression="gzip", engine="pyarrow")
        return base64.b64encode(ret_buffer).decode("utf-8")

    @classmethod
    def __serialize_using_to_dict(cls, df):
        return {"records": df.to_dict("records"), "columns": df.columns}

    @classmethod
    def serialize(cls, prop, engine="to_dict"):
        supportedEngines = {
            "fastparquet": DataFrameSerializer.__serialize_using_fastparquet,
            "pyarrow": DataFrameSerializer.__serialize_using_pyarrow,
            "to_dict": DataFrameSerializer.__serialize_using_to_dict,
        }
        return {
            PROP_TYPE: "pd.DataFrame",
            PROP_VALUE: supportedEngines[engine](prop),
            PROP_ENGINE: engine,
        }

    @classmethod
    def deserialize(cls, prop):
        [engine, value] = [
            prop[PROP_ENGINE],
            prop[PROP_VALUE],
        ]
        if engine == "to_dict":
            return DataFrame.from_records(value["records"], columns=value["columns"])
        return pd.read_parquet(io.BytesIO(value), engine)


class DashSerializer:
    @classmethod
    def serialize_value(cls, value):
        if isinstance(value, pd.DataFrame):
            # return serializer.serialize(prop, engine="pyarrow")
            # return DataFrameSerializer.serialize(value, engine="to_dict")
            return DataFrameSerializer.serialize(value, engine="fastparquet")
        return value

    @classmethod
    def serialize_prop(cls, component, propName):
        serializeFn = getattr(component, "serialize", None)
        if serializeFn:
            return serializeFn()

        propValue = getattr(component, propName)
        if isinstance(propValue, pd.DataFrame):
            # return serializer.serialize(prop, engine="pyarrow")
            # return DataFrameSerializer.serialize(propValue, engine="to_dict")
            return DataFrameSerializer.serialize(propValue, engine="fastparquet")
        return propValue

    @classmethod
    def deserialize_value(cls, prop):
        deserializeFn = getattr(prop, "deserialize", None)
        if deserializeFn:
            return deserializeFn()

        try:
            jsonObj = json.loads(prop) if isinstance(prop, str) else prop
            _type = (
                jsonObj[PROP_TYPE]
                if isinstance(jsonObj, dict) and PROP_TYPE in jsonObj
                else None
            )
            if _type == "pd.DataFrame":
                return DataFrameSerializer.deserialize(jsonObj)
        except ValueError:
            pass

        return prop

    @classmethod
    def deserialize(cls, obj):
        props = obj if isinstance(obj, list) else [obj]
        return [
            (
                {**prop, "value": DashSerializer.deserialize_value(prop["value"])}
                if "value" in prop
                else prop
            )
            for prop in props
        ]
