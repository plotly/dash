class DashException(Exception):
    pass


class CallbackException(DashException):
    pass


class NonExistantIdException(CallbackException):
    pass


class NonExistantPropException(CallbackException):
    pass


class NonExistantEventException(CallbackException):
    pass


class UndefinedLayoutException(CallbackException):
    pass


class IncorrectTypeException(CallbackException):
    pass


class MissingEventsException(CallbackException):
    pass


class LayoutIsNotDefined(CallbackException):
    pass


class IDsCantContainPeriods(CallbackException):
    pass

class CantHaveMultipleOutputs(CallbackException):
    pass
