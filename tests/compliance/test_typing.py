import os
import shlex
import subprocess
import sys
import json
import sysconfig

import pytest

component_template = """
from dash_generator_test_component_typescript import TypeScriptComponent

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
    config_file_to_cleanup = None

    # For pyright, create a pyrightconfig.json to help it find installed packages
    # and adjust the command to use relative path
    if module == "pyright":
        config_dir = os.path.dirname(codefile)
        config_file = os.path.join(config_dir, "pyrightconfig.json")

        # For editable installs, we need to find the actual source location
        # The test component is installed as an editable package
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

        # Get the site-packages directory for standard packages
        site_packages = sysconfig.get_path("purelib")

        # Check if dash is installed as editable or regular install
        # If editable, we need project root first; if regular, site-packages first
        import dash

        dash_file = dash.__file__
        is_editable = project_root in dash_file

        if is_editable:
            # Editable install: prioritize project root
            extra_paths = [project_root, site_packages]
        else:
            # Regular install (CI): prioritize site-packages
            extra_paths = [site_packages, project_root]

        # Add the test component source directories
        # They are in the @plotly subdirectory of the project root
        test_components_dir = os.path.join(project_root, "@plotly")

        if os.path.exists(test_components_dir):
            for component in os.listdir(test_components_dir):
                component_path = os.path.join(test_components_dir, component)
                if os.path.isdir(component_path):
                    extra_paths.append(component_path)

        # For files in /tmp (component tests), we need a different approach
        # Include the directory containing the test file
        test_file_dir = os.path.dirname(codefile)

        config = {
            "pythonVersion": f"{sys.version_info.major}.{sys.version_info.minor}",
            "pythonPlatform": sys.platform,
            "executionEnvironments": [
                {"root": project_root, "extraPaths": extra_paths},
                {"root": test_file_dir, "extraPaths": extra_paths},
            ],
        }

        # Write config to project root instead of test directory
        config_file = os.path.join(project_root, "pyrightconfig.json")
        config_file_to_cleanup = config_file  # Store for cleanup later
        with open(config_file, "w") as f:
            json.dump(config, f)

        # Run pyright from project root with absolute path to test file
        codefile_arg = codefile
        cwd = project_root
    else:
        codefile_arg = codefile
        cwd = None

    cmd = shlex.split(
        f"{sys.executable} -m {module} {codefile_arg}{extra}",
        posix=sys.platform != "win32",
        comments=True,
    )

    env = os.environ.copy()

    # For mypy, set MYPYPATH to help it find editable installs
    # Note: mypy doesn't want site-packages in MYPYPATH
    if module == "mypy":
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        test_components_dir = os.path.join(project_root, "@plotly")

        mypy_paths = [project_root]
        if os.path.exists(test_components_dir):
            for component in os.listdir(test_components_dir):
                component_path = os.path.join(test_components_dir, component)
                if os.path.isdir(component_path):
                    mypy_paths.append(component_path)

        env["MYPYPATH"] = os.pathsep.join(mypy_paths)

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=cwd,
    )
    out, err = proc.communicate()

    # Cleanup pyrightconfig.json if we created it
    if config_file_to_cleanup and os.path.exists(config_file_to_cleanup):
        try:
            os.remove(config_file_to_cleanup)
        except OSError:
            pass  # Ignore cleanup errors

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


@pytest.fixture()
def change_dir():
    original_dir = os.getcwd()

    def change(dirname):
        os.chdir(dirname)

    yield change

    os.chdir(original_dir)


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
        pytest.param(
            "element=set()",
            {
                "expected_status": 1,
            },
            marks=pytest.mark.skip(reason="Ignoring element=set() test case"),
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
