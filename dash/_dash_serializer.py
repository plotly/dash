import base64
import json
from typing import cast

# from os import remove
import uuid
import random
import io
import pandas as pd
from pandas.core.frame import DataFrame
import pyarrow as pa


srd = random.Random(0)


PROP_TYPE = "__type"
PROP_VALUE = "__value"
PROP_ENGINE = "__engine"
PROP_ID = "__internal_id"


class NotSerializable(Exception):
    pass


class DataFrameSerializer:
    def __serialize_using_fastparquet(self, df, internal_id):
        outputPath = "{}.fastparquet".format(internal_id)
        df.to_parquet(
            outputPath, compression="gzip", engine="fastparquet"
        )  # TODO: check https://pandas.pydata.org/pandas-docs/dev/reference/api/pandas.DataFrame.to_parquet.html
        with open(outputPath, "rb") as f:
            buffer_val = f.read()
            f.close()
            # remove(outputPath)
        return base64.b64encode(buffer_val).decode("utf-8")

    def pyarrow_table_to_bytes(self, table: pa.Table) -> bytes:
        sink = pa.BufferOutputStream()
        writer = pa.RecordBatchStreamWriter(sink, table.schema)
        writer.write_table(table)
        writer.close()
        byteData = cast(bytes, sink.getvalue().to_pybytes())
        return base64.b64encode(byteData).decode("utf-8")

    def __serialize_using_pyarrow(
        self, df, internal_id, useFile=False, useParquetFormat=False
    ):
        if not useParquetFormat:
            table = pa.Table.from_pandas(df)
            return self.pyarrow_table_to_bytes(table)
        elif useFile:
            outputPath = "{}.pyarrow".format(internal_id)
            df.to_parquet(outputPath, compression="gzip", engine="pyarrow")
            with open(outputPath, "rb") as f:
                buffer_val = f.read()
                f.close()
                # remove(outputPath)
            return base64.b64encode(buffer_val).decode("utf-8")
        else:
            ret_buffer = df.to_parquet(compression="gzip", engine="pyarrow")
            return base64.b64encode(ret_buffer).decode("utf-8")

    def serialize(self, prop, internal_id, engine="fastparquet"):
        if engine == "fastparquet":
            serialized_value = self.__serialize_using_fastparquet(prop, internal_id)
        elif engine == "pyarrow":
            serialized_value = self.__serialize_using_pyarrow(prop, internal_id)
        else:
            serialized_value = {'records': prop.to_dict("records"), 'columns': prop.columns}
        return {
            PROP_TYPE: "pd.DataFrame",
            PROP_VALUE: serialized_value,
            PROP_ENGINE: engine,
            PROP_ID: internal_id,
        }

    def deserialize(self, prop):
        # TODO: Consider partial updates? - use _id to find from file for original/full DataFrame, then apply patch only?
        [engine, _internal_id, value] = [
            prop[PROP_ENGINE],
            prop[PROP_ID],
            prop[PROP_VALUE],
        ]
        if engine == "to_dict":
            return DataFrame.from_records(value)
        else:
            return pd.read_parquet(io.BytesIO(value), engine)


class DashSerializer:
    @classmethod
    def __serialize_value(cls, prop):
        try:
            serializeFn = getattr(prop, "serialize")
            return serializeFn()
        except AttributeError:
            pass

        if isinstance(prop, pd.DataFrame):
            internal_id = str(uuid.UUID(int=srd.randint(0, 2 ** 128)))
            serializer = DataFrameSerializer()
            # return serializer.serialize(prop, internal_id, engine="pyarrow")
            return serializer.serialize(prop, internal_id, engine="to_dict")
        raise NotSerializable

    @classmethod
    def __deserialize_value(cls, prop):
        try:
            deserializeFn = getattr(prop, "deserialize")
            return deserializeFn()
        except AttributeError:
            pass
        try:
            jsonObj = json.loads(prop) if isinstance(prop, str) else prop
            _type = (
                jsonObj[PROP_TYPE]
                if isinstance(jsonObj, dict) and PROP_TYPE in jsonObj
                else None
            )
            if _type == "pd.DataFrame":
                return DataFrameSerializer().deserialize(jsonObj)
        except AttributeError:
            pass
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
        try:
            return DashSerializer.__serialize_value(obj)
        except NotSerializable:
            pass

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
