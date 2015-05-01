import os

import pytest


class TestMarkerlib:

    @pytest.mark.importorskip('ast')
    def test_markers(self):
        from _markerlib import interpret, default_environment, compile

        os_name = os.name

        assert interpret("")

        assert interpret("os.name != 'buuuu'")
        assert interpret("os_name != 'buuuu'")
        assert interpret("python_version > '1.0'")
        assert interpret("python_version < '5.0'")
        assert interpret("python_version <= '5.0'")
        assert interpret("python_version >= '1.0'")
        assert interpret("'%s' in os.name" % os_name)
        assert interpret("'%s' in os_name" % os_name)
        assert interpret("'buuuu' not in os.name")

        assert not interpret("os.name == 'buuuu'")
        assert not interpret("os_name == 'buuuu'")
        assert not interpret("python_version < '1.0'")
        assert not interpret("python_version > '5.0'")
        assert not interpret("python_version >= '5.0'")
        assert not interpret("python_version <= '1.0'")
        assert not interpret("'%s' not in os.name" % os_name)
        assert not interpret("'buuuu' in os.name and python_version >= '5.0'")
        assert not interpret("'buuuu' in os_name and python_version >= '5.0'")

        environment = default_environment()
        environment['extra'] = 'test'
        assert interpret("extra == 'test'", environment)
        assert not interpret("extra == 'doc'", environment)

        def raises_nameError():
            try:
                interpret("python.version == '42'")
            except NameError:
                pass
            else:
                raise Exception("Expected NameError")

        raises_nameError()

        def raises_syntaxError():
            try:
                interpret("(x for x in (4,))")
            except SyntaxError:
                pass
            else:
                raise Exception("Expected SyntaxError")

        raises_syntaxError()

        statement = "python_version == '5'"
        assert compile(statement).__doc__ == statement

