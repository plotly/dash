import json
import pandas as pd


class DashSerializer:
    @classmethod
    def serialize(cls, prop):
        if isinstance(prop, pd.DataFrame):
            return {"__type": "DataFrame", "__value": prop.to_dict("records")}

        return prop

    @classmethod
    def deserialize(cls, prop):
        obj = json.loads(prop)
        __type = obj["__type"] if hasattr(obj, "__type") else None
        if __type == "DataFrame":
            return pd.DataFrame(obj["__value"])

        return prop

    @classmethod
    def serialize_tree(cls, obj):
        if isinstance(obj, pd.DataFrame):
            return cls.serialize(obj)

        # Plotly
        try:
            obj = obj.to_plotly_json()
        except AttributeError:
            pass

        if isinstance(obj, (list, tuple)):
            if obj:
                # Must process list recursively even though it may be slow
                return [cls.serialize_tree(v) for v in obj]

        # Recurse into lists and dictionaries
        if isinstance(obj, dict):
            return {k: cls.serialize_tree(v) for k, v in obj.items()}

        return obj
