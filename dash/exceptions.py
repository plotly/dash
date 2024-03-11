from textwrap import dedent


class DashException(Exception):
    def __init__(self, msg=""):
        super().__init__(dedent(msg).strip())


class ObsoleteKwargException(DashException):
    pass


class NoLayoutException(DashException):
    pass


class CallbackException(DashException):
    pass


class NonExistentEventException(CallbackException):
    pass


class IncorrectTypeException(CallbackException):
    pass


class IDsCantContainPeriods(CallbackException):
    pass


class WildcardInLongCallback(CallbackException):
    pass


# Better error name now that more than periods are not permitted.
class InvalidComponentIdError(IDsCantContainPeriods):
    pass


class PreventUpdate(CallbackException):
    pass


class DuplicateIdError(DashException):
    pass


class InvalidCallbackReturnValue(CallbackException):
    pass


class InvalidConfig(DashException):
    pass


class InvalidResourceError(DashException):
    pass


class InvalidIndexException(DashException):
    pass


class DependencyException(DashException):
    pass


class ResourceException(DashException):
    pass


class MissingCallbackContextException(CallbackException):
    pass


class UnsupportedRelativePath(CallbackException):
    pass


class ProxyError(DashException):
    pass


class DuplicateCallback(DashException):
    pass


class LongCallbackError(DashException):
    pass


class MissingLongCallbackManagerError(DashException):
    pass


class PageError(DashException):
    pass


class ImportedInsideCallbackError(DashException):
    pass
