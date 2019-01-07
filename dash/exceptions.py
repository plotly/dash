class DashException(Exception):
    pass


class NoLayoutException(DashException):
    pass


class CallbackException(DashException):
    pass


class NonExistentIdException(CallbackException):
    pass


class NonExistentPropException(CallbackException):
    pass


class NonExistentEventException(CallbackException):
    pass


class UndefinedLayoutException(CallbackException):
    pass


class IncorrectTypeException(CallbackException):
    pass


class MissingInputsException(CallbackException):
    pass


class LayoutIsNotDefined(CallbackException):
    pass


class IDsCantContainPeriods(CallbackException):
    pass


class CantHaveMultipleOutputs(CallbackException):
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
