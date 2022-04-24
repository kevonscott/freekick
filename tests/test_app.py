import unittest
from flask import Flask
import freekick.app


class AppTestCase(unittest.TestCase):
    def test_create_app(self):
        """Test to confirm that a flask app gets created."""
        app = freekick.app.create_app()
        self.assertIsInstance(app, Flask)
