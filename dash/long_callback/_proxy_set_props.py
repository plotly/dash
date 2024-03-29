class ProxySetProps(dict):
    def __init__(self, on_change):
        super().__init__()
        self.on_change = on_change

    def __setitem__(self, key, value):
        self.on_change(key, value)
