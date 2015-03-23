import unittest
import reflex_interactive_app as rapp
import sys
import contextlib
from StringIO import StringIO


@contextlib.contextmanager
def redirect_stdout(stdout=None):
    oldstdout = sys.stdout
    sys.stdout = stdout
    yield
    sys.stdout = oldstdout


class TestInteractiveAppBase(unittest.TestCase):

    def setUp(self):
        self.orig_argv = sys.argv[:]
        del sys.argv[1:]

    def tearDown(self):
        sys.argv = self.orig_argv[:]

    def test_basic(self):
        sys.argv.append('--in_sof=test')
        sys.argv.append('--in_sop=test')
        sys.argv.append('--in_sof_rec_orig=test')
        rapp.PipelineInteractiveApp()


class TestInteractiveApp(TestInteractiveAppBase):

    def setUp(self):
        TestInteractiveAppBase.setUp(self)
        sys.argv.append('--in_sof=test')
        sys.argv.append('--in_sop=test')
        sys.argv.append('--in_sof_rec_orig=test')
        self.app = rapp.PipelineInteractiveApp()

    def test_setEnableGUI(self):
        self.app.setEnableGUI('true')
        self.assertEqual(self.app.inputs.enable, 'TRUE')
        self.app.setEnableGUI('FALSE')
        self.assertEqual(self.app.inputs.enable, 'FALSE')
        self.app.setEnableGUI(u'true')
        self.assertEqual(self.app.inputs.enable, 'TRUE')
        self.app.setEnableGUI(u'FALSE')
        self.assertEqual(self.app.inputs.enable, 'FALSE')
        self.app.setEnableGUI(True)
        self.assertEqual(self.app.inputs.enable, 'TRUE')
        self.app.setEnableGUI(False)
        self.assertEqual(self.app.inputs.enable, 'FALSE')

    def test_output(self):
        import json
        out = StringIO()
        with redirect_stdout(out):
            self.app.print_outputs()
        # TODO: test with some proper output
        self.assertEqual(json.loads(out.getvalue()), {})


class TestDependenciesMissing(TestInteractiveApp):

    def setUp(self):
        import __builtin__ as builtins
        TestInteractiveApp.setUp(self)
        # fail wx imports
        self.origimport = builtins.__import__

        def failimport(name, globals={}, locals={}, fromlist=[], level=-1):
            if name == 'wx':
                raise ImportError('Could not import ' + name)
            return self.origimport(name, globals, locals, fromlist, level)

        builtins.__import__ = failimport

    def tearDown(self):
        import __builtin__ as builtins
        builtins.__import__ = self.origimport
        TestInteractiveApp.tearDown(self)

    def test_isGUIEnabled(self):
        self.app.setEnableGUI(True)
        self.assertFalse(self.app.isGUIEnabled())

if __name__ == "__main__":
    unittest.main()
