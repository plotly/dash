import base64
import json
import pandas as pd

PROP_TYPE = "__type"
PROP_VALUE = "__value"
PROP_ENGINE = "__engine"


class NotSerializable(Exception):
    pass


class DashSerializer:
    @classmethod
    def __serialize_value(cls, prop):
        try:
            serializeFn = getattr(prop, "serialize")
            return serializeFn()
        except AttributeError:
            pass

        if isinstance(prop, pd.DataFrame):
            engine = "pyarrow"
            buffer_val = prop.to_parquet(compression="gzip", engine=engine)
            return {
                PROP_TYPE: "pd.DataFrame",
                PROP_VALUE: base64.b64encode(buffer_val).decode("utf-8"),
                PROP_ENGINE: engine,
            }

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
            obj = (
                jsonObj
                if isinstance(jsonObj, dict) and PROP_TYPE in jsonObj
                else {PROP_TYPE: None, PROP_ENGINE: None}
            )
            [_type, _engine] = [obj[PROP_TYPE], obj[PROP_ENGINE]]
            if _type == "pd.DataFrame":
                return pd.read_parquet(obj[PROP_VALUE], _engine)
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
