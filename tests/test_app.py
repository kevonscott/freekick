import unittest
import sys

from flask import Flask

sys.path.append(".")
import freekick.app  # noqa E402


class AppTestCase(unittest.TestCase):
    def test_create_app(self):
        """Test to confirm that a flask app gets created."""
        app = freekick.app.create_app()
        self.assertIsInstance(app, Flask)
