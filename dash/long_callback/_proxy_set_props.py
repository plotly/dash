class ProxySetProps(dict):
    """
    Defer dictionary item setter to run a custom function on change.
    Used by background callback manager to save the `set_props` data.
    """

    def __init__(self, on_change):
        super().__init__()
        self.on_change = on_change

    def __setitem__(self, key, value):
        self.on_change(key, value)
