import os
import sys
import unittest


class TestDashImport(unittest.TestCase):
    def setUp(self):
        with open("dash.py", "w") as _:
            pass

    def tearDown(self):
        try:
            os.remove("dash.py")
            os.remove("dash.pyc")
        except OSError:
            pass

    @unittest.skipIf(sys.version_info[0] == 2, "only run in python3")
    def test_dash_import(self):
        """Test that program exits if the wrong dash module was imported"""

        with self.assertRaises(SystemExit) as cm:
            import dash_core_components  # noqa

        self.assertEqual(cm.exception.code, 1)
