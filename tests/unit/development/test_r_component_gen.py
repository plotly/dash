import os
import shutil
import re
from textwrap import dedent

import pytest

from dash.development._r_components_generation import make_namespace_exports


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
