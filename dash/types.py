import typing
from typing import Any, Dict, List, Union

from pydantic import Field, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import core_schema
from typing_extensions import Annotated, TypedDict, NotRequired


class _NumberSchema:  # pylint: disable=too-few-public-methods
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> Any:
        return core_schema.float_schema()

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _schema: Any, _handler: GetJsonSchemaHandler
    ) -> dict:
        return {"type": "number"}


NumberType = Annotated[
    Union[typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex],
    _NumberSchema,
]


class RendererHooks(TypedDict):  # pylint: disable=too-many-ancestors
    layout_pre: NotRequired[str]
    layout_post: NotRequired[str]
    request_pre: NotRequired[str]
    request_post: NotRequired[str]
    callback_resolved: NotRequired[str]
    request_refresh_jwt: NotRequired[str]


class CallbackDependency(TypedDict):
    id: Union[str, Dict[str, Any]]
    property: str


class CallbackInput(TypedDict):
    id: Union[str, Dict[str, Any]]
    property: str
    value: Any


class CallbackDispatchBody(TypedDict):
    output: str
    outputs: List[CallbackDependency]
    inputs: List[CallbackInput]
    state: List[CallbackInput]
    changedPropIds: List[str]


CallbackOutput = Annotated[
    Dict[str, Any],
    Field(
        description="The return values of the callback. A mapping of component & property names to their updated values."
    ),
]

CallbackSideOutput = Annotated[
    Dict[str, Any],
    Field(
        description="Side-effect updates that the callback performed but did not declare ahead of time. A mapping of component & property names to their updated values."
    ),
]


class CallbackDispatchResponse(TypedDict):
    multi: NotRequired[bool]
    response: NotRequired[Dict[str, CallbackOutput]]
    sideUpdate: NotRequired[Dict[str, CallbackSideOutput]]
    dist: NotRequired[List[Any]]
