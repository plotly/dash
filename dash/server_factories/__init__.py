# python
import contextvars

_request_adapter_var = contextvars.ContextVar("request_adapter")

def set_request_adapter(adapter):
    _request_adapter_var.set(adapter)

def get_request_adapter():
    return _request_adapter_var.get()
