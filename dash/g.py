from ._shared_callback_ops import _register_callback

_CALLBACK_LIST = []
_CALLBACK_MAP = {}
    
class app:
    def callback(*args, **kwargs):
        return _register_callback(
            _CALLBACK_LIST, _CALLBACK_MAP, False,
            *args, **kwargs
        )
