import unittest
from flask import Flask
import freekick.app

import sys

sys.path.append("..")


class AppTestCase(unittest.TestCase):
    def test_create_app(self):
        """Test to confirm that a flask app gets created."""
        app1 = freekick.app.create_app()
        self.assertIsInstance(app1, Flask)
