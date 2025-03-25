# pylint: disable=too-few-public-methods
from .exceptions import ObsoleteAttributeException


class ObsoleteAttribute:
    def __init__(self, message: str, exc=ObsoleteAttributeException):
        self.message = message
        self.exc = exc


class ObsoleteChecker:
    _obsolete_attributes = {
        "run_server": ObsoleteAttribute("app.run_server has been replaced by app.run"),
        "long_callback": ObsoleteAttribute(
            "app.long_callback has been  removed, use app.callback(..., background=True) instead"
        ),
    }

    def __getattr__(self, name: str):
        if name in self._obsolete_attributes:
            err = self._obsolete_attributes[name]
            raise err.exc(err.message)
        return getattr(self.__dict__, name)
