import os

from flask import jsonify, request

from dash import Dash, Input, Output, callback, ctx, html

POD = os.environ.get("POD", "?")

app = Dash(__name__)
server = app.server

app.layout = html.Div(
    [
        html.Div(f"pod {POD}", id="pod"),
        html.Button("add", id="add"),
        html.Div(id="count"),
    ]
)


@callback(Output("count", "children"), Input("add", "n_clicks"))
def add(n_clicks):
    store = ctx.shared_storage
    value = store.get("count", 0)
    if n_clicks:
        value += 1
        store.set("count", value)
    return f"count={value}"


@server.route("/whoami")
def whoami():
    store = app.shared_storage
    try:
        # A worker without the lock learns of an owner change on its next call.
        store.get("whoami")
    except Exception:  # pylint: disable=broad-except
        pass
    coord = store._coord  # pylint: disable=protected-access
    return jsonify(
        pod=POD,
        pid=os.getpid(),
        role=coord._role,  # pylint: disable=protected-access
        token=coord.token,
        holds_lock=coord._cluster is not None,  # pylint: disable=protected-access
        address=list(coord._address or ()),  # pylint: disable=protected-access
        conn_token=store._conn_token,  # pylint: disable=protected-access
        lock=_lock_view(coord._cluster),  # pylint: disable=protected-access
    )


def _lock_view(lock):
    if lock is None:
        return None
    state = lock._state  # pylint: disable=protected-access
    return {
        "id": lock.id,
        "role": state.role,
        "term": state.term,
        "owner_id": state.owner_id,
        "owner_addr": list(state.owner_addr or ()),
    }


@server.route("/kv/<key>", methods=["GET", "POST"])
def kv(key):
    store = app.shared_storage
    if request.method == "POST":
        store.set(key, request.get_json()["value"])
        return jsonify(ok=True, pid=os.getpid())
    return jsonify(value=store.get(key), pid=os.getpid())


@server.route("/pub/<topic>", methods=["POST"])
def pub(topic):
    app.shared_storage.publish(topic, request.get_json()["message"])
    return jsonify(ok=True)


@server.route("/poll/<topic>")
def poll(topic):
    sub = app.shared_storage.subscribe(topic, replay_from=int(request.args["from"]))
    try:
        return jsonify(pairs=sub.poll(timeout=2), pid=os.getpid())
    except Exception as err:  # pylint: disable=broad-except
        return jsonify(error=type(err).__name__, pid=os.getpid())
    finally:
        sub.close()
