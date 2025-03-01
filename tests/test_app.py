import logging
import unittest

from flask import Flask

from tests import ensure_test_env
from freekick.app import create_app

class AppTestCase(unittest.TestCase):
    def test_create_app(self):
        """Test to confirm that a flask app gets created."""
        app = create_app(mode="DEVELOPMENT", init_wpc_pyth=False)
        self.assertIsInstance(app, Flask)
        self.assertTrue(
            logging.getLevelName(app.logger.getEffectiveLevel()) == "DEBUG"
        )
