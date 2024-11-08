from typing_extensions import TypedDict, NotRequired


class RendererHooks(TypedDict):  # pylint: disable=too-many-ancestors
    layout_pre: NotRequired[str]
    layout_post: NotRequired[str]
    request_pre: NotRequired[str]
    request_post: NotRequired[str]
    callback_resolved: NotRequired[str]
    request_refresh_jwt: NotRequired[str]
