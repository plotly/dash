import json

import pandas as pd

PROP_TYPE = "__type"
PROP_VALUE = "__value"
PROP_ENGINE = "__engine"


class DataFrameSerializer:
    @classmethod
    def __serialize_using_to_dict(cls, df):
        return {"records": df.to_dict("records"), "columns": df.columns}

    @classmethod
    def serialize(cls, prop, engine="to_dict"):
        supportedEngines = {
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
            return pd.DataFrame.from_records(value["records"], columns=value["columns"])
        return prop


class DashSerializer:
    @classmethod
    def serialize_value(cls, value):
        if isinstance(value, pd.DataFrame):
            return DataFrameSerializer.serialize(value, engine="to_dict")
        return value

    @classmethod
    def serialize_prop(cls, component, propName):
        serializeFn = getattr(component, "serialize", None)
        if serializeFn:
            return serializeFn()

        propValue = getattr(component, propName)
        if isinstance(propValue, pd.DataFrame):
            return DataFrameSerializer.serialize(propValue, engine="to_dict")
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
