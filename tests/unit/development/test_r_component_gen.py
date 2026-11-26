import os
import shutil
import re
import sys
import types
from textwrap import dedent

import pytest

from dash.development import _r_components_generation
from dash.development._r_components_generation import (
    generate_rpkg,
    make_namespace_exports,
)


@pytest.fixture
def make_r_dir():
    os.makedirs("R")

    yield

    shutil.rmtree("R")


def test_r_exports(make_r_dir):
    extra_file = dedent(
        """
        # normal function syntax
        my_func <- function(a, b) {
            c <- a + b
            nested_func <- function() { stop("no!") }
            another_to_exclude = function(d) { d * d }
            another_to_exclude(c)
        }

        # indented (no reason but we should allow) and using = instead of <-
        # also braces in comments enclosing it {
            my_func2 = function() {
                s <- "unmatched closing brace }"
                ignore_please <- function() { 1 }
            }
        # }

        # real example from dash-table that should exclude FUN
        df_to_list <- function(df) {
          if(!(is.data.frame(df)))
            stop("!")
          setNames(lapply(split(df, seq(nrow(df))),
                          FUN = function (x) {
                            as.list(x)
                          }), NULL)
        }

        # single-line compressed
        util<-function(x){x+1}

        # prefix with . to tell us to ignore
        .secret <- function() { stop("You can't see me") }

        # . in the middle is OK though
        not.secret <- function() { 42 }
    """
    )

    components = ["Component1", "Component2"]
    prefix = "pre"

    expected_exports = [prefix + c for c in components] + [
        "my_func",
        "my_func2",
        "df_to_list",
        "util",
        "not.secret",
    ]

    mock_component_file = dedent(
        """
        nope <- function() { stop("we don't look in component files") }
    """
    )

    with open(os.path.join("R", "preComponent1.R"), "w") as f:
        f.write(mock_component_file)

    with open(os.path.join("R", "extras.R"), "w") as f:
        f.write(extra_file)

    exports = make_namespace_exports(components, prefix)
    print(exports)
    matches = re.findall(r"export\(([^()]+)\)", exports.replace("\n", " "))

    assert matches == expected_exports


def generate_description(author, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    os.makedirs("man")
    # generate_rpkg imports the component package to read its JS dependencies
    my_lib = types.ModuleType("my_lib")
    my_lib._js_dist = [{"relative_package_path": "my_lib.min.js"}]
    monkeypatch.setitem(sys.modules, "my_lib", my_lib)
    monkeypatch.setattr(sys, "path", sys.path[:])
    generate_rpkg(
        {"name": "my-lib", "version": "1.0.0", "author": author},
        {"pkg_help_title": "My Lib", "pkg_help_description": "My Lib"},
        "my_lib",
        "",
        "",
        "",
        "",
        False,
    )
    return (
        (tmp_path / "DESCRIPTION").read_text(),
        (tmp_path / "man" / "myLib-package.Rd").read_text(),
    )


@pytest.mark.parametrize(
    "author",
    [
        "Barney Rubble <b@rubble.com>",
        "Barney Rubble <b@rubble.com> (http://barnyrubble.tumblr.com/)",
        {"name": "Barney Rubble", "email": "b@rubble.com"},
        {
            "name": "Barney Rubble",
            "email": "b@rubble.com",
            "url": "http://barnyrubble.tumblr.com/",
        },
    ],
)
def test_r_author_formats(author, tmp_path, monkeypatch):
    description, package_help = generate_description(author, tmp_path, monkeypatch)

    assert (
        'Authors@R: person("Barney", "Rubble", role = c("aut", "cre"), '
        'email = "b@rubble.com")'
    ) in description
    assert "Maintainer}: Barney Rubble <b@rubble.com>" in package_help


@pytest.mark.parametrize("author", ["Barney Rubble", {"name": "Barney Rubble"}])
def test_r_author_without_email(author, tmp_path, monkeypatch, capsys):
    with pytest.raises(SystemExit):
        generate_description(author, tmp_path, monkeypatch)

    assert "email" in capsys.readouterr().err


@pytest.mark.parametrize(
    "rpkg_data, title, description",
    [
        (None, "From package.json", "From package.json"),
        ({}, "From package.json", "From package.json"),
        ({"pkg_help_title": "R title"}, "R title", "From package.json"),
        (
            {"pkg_help_title": "R title", "pkg_help_description": "R desc"},
            "R title",
            "R desc",
        ),
    ],
)
def test_r_description_title_fallback(
    tmp_path, monkeypatch, rpkg_data, title, description
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(_r_components_generation, "write_js_metadata", lambda *a: None)
    os.makedirs("man")
    pkg_data = {
        "name": "my-pkg",
        "version": "1.0.0",
        "description": "From package.json",
        "author": "Jane Doe <jane@example.com>",
        "license": "MIT",
    }

    generate_rpkg(pkg_data, rpkg_data, "my_pkg", "", "", "", "", False)

    content = (tmp_path / "DESCRIPTION").read_text()
    assert "Title: {}\n".format(title) in content
    assert "Description: {}\n".format(description) in content
