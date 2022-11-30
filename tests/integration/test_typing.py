import os
import shlex
import subprocess
import sys

import pytest

component_template = """
from dash_generator_test_component_typescript.TypeScriptComponent import TypeScriptComponent

t = TypeScriptComponent({0})
"""


def run_pyright(codefile):

    cmd = shlex.split(
        f"pyright {codefile}",
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


def assert_pyright_output(
    codefile, expected_outputs=tuple(), expected_errors=tuple(), expected_status=0
):
    output, error, status = run_pyright(codefile)
    assert (
        status == expected_status
    ), f"Status: {status}\nOutput: {output}\nError: {error}"
    for ex_out in expected_outputs:
        assert ex_out in output
    for ex_err in expected_errors:
        assert ex_err in error


@pytest.mark.skipif(sys.version_info < (3, 7), reason="pyright not available on 3.6")
@pytest.mark.parametrize(
    "arguments, assertions",
    [
        (
            "a_string=4",
            {
                "expected_status": 1,
                "expected_outputs": [
                    'Argument of type "Literal[4]" cannot be assigned to parameter "a_string" of type "str"'
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
                    'Argument of type "Literal[\'\']" cannot be assigned to parameter "a_number" '
                    'of type "int | float | Number"'
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
                    'of type "List[str]"'
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
                    'to parameter "a_tuple" of type "Tuple[int | float | Number, str]"'
                ],
            },
        ),
        (
            "a_tuple=(1, 'tuple')",
            {
                "expected_status": 0,
            },
        ),
    ],
)
def test_component_typing(arguments, assertions, tmp_path):
    codefile = os.path.join(tmp_path, "code.py")
    with open(codefile, "w") as f:
        f.write(component_template.format(arguments))

    assert_pyright_output(codefile, **assertions)
