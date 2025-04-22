import os
import shlex
import subprocess
import sys

import pytest

component_template = """
from dash_generator_test_component_typescript.TypeScriptComponent import TypeScriptComponent

t = TypeScriptComponent({0})
"""

basic_app_template = """
from dash import Dash, html, dcc, callback, Input, Output

app = Dash()

{0}
app.layout = {1}

@callback(Output("out", "children"), Input("btn", "n_clicks"))
def on_click() -> html.Div:
    return {2}
"""

valid_layout = """html.Div([
    html.H2('Valid'),
    'String in middle',
    123,
    404.4,
    dcc.Input(value='', id='in')
])
"""
valid_layout_list = """[
    html.H2('Valid'),
    'String in middle',
    123,
    404.4,
    dcc.Input(value='', id='in')
]
"""
valid_layout_function = """
def layout() -> html.Div:
    return html.Div(["hello layout"])

"""

invalid_layout = """html.Div([
    {"invalid": "dictionary in children"}
])
"""
# There is not invalid layout for function & list as explicitly typed as Any to avoid special cases.

valid_callback = "html.Div('Valid')"
invalid_callback = "[]"


def run_module(codefile: str, module: str, extra: str = ""):

    cmd = shlex.split(
        f"{sys.executable} -m {module} {codefile}{extra}",
        posix=sys.platform != "win32",
        comments=True,
    )

    env = os.environ.copy()

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    out, err = proc.communicate()
    return out.decode(), err.decode(), proc.poll()


def assert_output(
    codefile: str,
    code: str,
    expected_outputs=tuple(),
    expected_errors=tuple(),
    expected_status=0,
    module="pyright",
):
    output, error, status = run_module(codefile, module)
    assert (
        status == expected_status
    ), f"Status: {status}\nOutput: {output}\nError: {error}\nCode: {code}"
    for ex_out in expected_outputs:
        assert ex_out in output, f"Invalid output:\n {output}\n\nCode: {code}"


def format_template_and_save(template, filename, *args):
    formatted = template.format(*args)
    with open(filename, "w") as f:
        f.write(formatted)
    return formatted


def expect(status=None, outputs=None, modular=False):
    data = {}
    if status is not None:
        data["expected_status"] = status
    if outputs is not None:
        data["expected_outputs"] = outputs
    if modular:
        # The expectations are per module.
        data["modular"] = modular
    return data


@pytest.mark.parametrize(
    "arguments, assertions",
    [
        (
            "a_string=4",
            {
                "expected_status": 1,
                "expected_outputs": [
                    'Argument of type "Literal[4]" cannot be assigned to parameter "a_string" of type "str | None"'
                ],
            },
        ),
        (
            "a_string='FooBar'",
            {
                "expected_status": 0,
            },
        ),
        (
            "a_number=''",
            {
                "expected_status": 1,
                "expected_outputs": [
                    'Argument of type "Literal[\'\']" cannot be assigned to parameter "a_number" ',
                    '"__float__" is not present',
                    '"__int__" is not present',
                    '"__complex__" is not present',
                ],
            },
        ),
        (
            "a_number=0",
            {
                "expected_status": 0,
            },
        ),
        (
            "a_number=2.2",
            {
                "expected_status": 0,
            },
        ),
        (
            "a_bool=4",
            {
                "expected_status": 1,
            },
        ),
        (
            "a_bool=True",
            {
                "expected_status": 0,
            },
        ),
        (
            "array_string={}",
            {
                "expected_status": 1,
                "expected_outputs": [
                    'Argument of type "dict[Any, Any]" cannot be assigned to parameter "array_string" '
                    'of type "Sequence[str] | None"'
                ],
            },
        ),
        (
            "array_string=[]",
            {
                "expected_status": 0,
            },
        ),
        (
            "array_string=[1,2,4]",
            {
                "expected_status": 1,
            },
        ),
        (
            "array_number=[1,2]",
            {
                "expected_status": 0,
            },
        ),
        (
            "array_number=['not','a', 'number']",
            {
                "expected_status": 1,
            },
        ),
        (
            "array_obj=[{'a': 'b'}]",
            {
                "expected_status": 0,
            },
        ),
        (
            "array_obj=[1]",
            {
                "expected_status": 1,
            },
        ),
        (
            "array_obj=[1, {}]",
            {
                "expected_status": 1,
            },
        ),
        (
            "union='Union'",
            {
                "expected_status": 0,
            },
        ),
        (
            "union=1",
            {
                "expected_status": 0,
            },
        ),
        (
            "union=0.42",
            {
                "expected_status": 0,
            },
        ),
        (
            "union=[]",
            {
                "expected_status": 1,
            },
        ),
        (
            "element=[]",
            {
                "expected_status": 0,
            },
        ),
        (
            "element=[TypeScriptComponent()]",
            {
                "expected_status": 0,
            },
        ),
        (
            "element=TypeScriptComponent()",
            {
                "expected_status": 0,
            },
        ),
        (
            "element=set()",
            {
                "expected_status": 1,
            },
        ),
        (
            "a_tuple=(1,2)",
            {
                "expected_status": 1,
                "expected_outputs": [
                    'Argument of type "tuple[Literal[1], Literal[2]]" cannot be assigned '
                    'to parameter "a_tuple" of type "Tuple[NumberType, str] | None'
                ],
            },
        ),
        (
            "a_tuple=(1, 'tuple')",
            {
                "expected_status": 0,
            },
        ),
        (
            "obj=set()",
            {
                "expected_status": 1,
            },
        ),
        (
            "obj={}",
            {
                "expected_status": 1,
                "expected_outputs": [
                    '"dict[Any, Any]" cannot be assigned to parameter "obj" of type "Obj | None"'
                ],
            },
        ),
        (
            "obj={'value': 'a', 'label': 1}",
            {
                "expected_status": 1,
                "expected_outputs": [
                    '"dict[str, str | int]" cannot be assigned to parameter "obj" of type "Obj | None"'
                ],
            },
        ),
        (
            "obj={'value': 'a', 'label': 'lab'}",
            {
                "expected_status": 0,
            },
        ),
    ],
)
def test_typi001_component_typing(arguments, assertions, tmp_path):
    codefile = os.path.join(tmp_path, "code.py")
    code = format_template_and_save(component_template, codefile, arguments)
    assert_output(codefile, code, module="pyright", **assertions)


typing_modules = ["pyright"]

if sys.version_info.minor >= 10:
    typing_modules.append("mypy")


@pytest.mark.parametrize("typing_module", typing_modules)
@pytest.mark.parametrize(
    "prelayout, layout, callback_return, assertions",
    [
        ("", valid_layout, valid_callback, expect(status=0)),
        ("", valid_layout_list, valid_callback, expect(status=0)),
        (valid_layout_function, "layout", valid_callback, expect(status=0)),
        ("", valid_layout, invalid_callback, expect(status=1)),
        ("", invalid_layout, valid_callback, expect(status=1)),
    ],
)
def test_typi002_typing_compliance(
    typing_module, prelayout, layout, callback_return, assertions, tmp_path
):
    codefile = os.path.join(tmp_path, "code.py")
    code = format_template_and_save(
        basic_app_template, codefile, prelayout, layout, callback_return
    )
    assert_output(codefile, code, module=typing_module, **assertions)
