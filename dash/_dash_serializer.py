import json
import pandas as pd


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
            return {"__type": "DataFrame", "__value": prop.to_dict("records")}
        else:
            raise NotSerializable

    @classmethod
    def __deserialize_value(cls, prop):
        try:
            deserializeFn = getattr(prop, "deserialize")
            return deserializeFn()
        except AttributeError:
            pass

        try:
            obj = json.loads(prop) if isinstance(prop, str) else prop
            __type = (
                obj["__type"] if isinstance(obj, dict) and "__type" in obj else None
            )
            if __type == "DataFrame":
                return pd.DataFrame(obj["__value"])
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
            return cls.__serialize_value(obj)
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
