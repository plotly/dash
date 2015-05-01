from __future__ import absolute_import

import textwrap


def DALS(s):
    "dedent and left-strip"
    return textwrap.dedent(s).lstrip()
