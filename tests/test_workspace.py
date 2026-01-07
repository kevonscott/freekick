from unittest import TestCase
import importlib

from tests import ensure_test_env  # noqa: F401
from freekick.datastore import League
from freekick.utils.workspace import DEFAULT_WORKSPACE_SETTINGS


class WorkspaceSyncTestCase(TestCase):

    def setUp(self):
        pass

    def test_all_league_has_default_estimator(self):
        for league in League:
            default_estimator = DEFAULT_WORKSPACE_SETTINGS['ESTIMATOR'].get(
                league.name, None
            )
            self.assertTrue(
                default_estimator and isinstance(default_estimator, str),
                f"No Default Estimator found for {league}!!"
            )

            # CHeck that we can import this class as the app expects exists
            fl = importlib.import_module("freekick.learners")
            # AttributeError if league does not exists in freekick.learners
            getattr(fl, default_estimator)

            # Check that persisted model exists
