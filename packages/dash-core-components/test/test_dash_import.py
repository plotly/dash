import os
import unittest


class TestDashImport(unittest.TestCase):
    def setUp(self):
        with open('dash.py', 'w') as f:
            pass        
        
    def tearDown(self):
        try:
            os.remove('dash.py')
            os.remove('dash.pyc')
        except OSError:
            pass
        
    def test_dash_import(self):
        """Test that program exits if the wrong dash module was imported"""
        
        with self.assertRaises(SystemExit) as cm:
            import dash_core_components

        self.assertEqual(cm.exception.code, 1)
