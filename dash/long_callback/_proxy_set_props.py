class ProxySetProps(dict):
    """
    Defer dictionary item setter to run a custom function on change.
    Used by background callback manager to save the `set_props` data.
    """

    def __init__(self, on_change):
        super().__init__()
        self.on_change = on_change
        self._data = {}

    def __setitem__(self, key, value):
        self.on_change(key, value)
        self._data.setdefault(key, {})
        self._data[key] = {**self._data[key], **value}

    def get(self, key):
        return self._data.get(key)
