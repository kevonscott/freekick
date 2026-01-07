import unittest
from parameterized import parameterized
from tests import ensure_test_env  # noqa: F401
from freekick.learners.learner_utils import League
from freekick.utils import load_config, get_default_estimator
from freekick import ESTIMATOR_LOCATION


class EstimatorTestCase(unittest.TestCase):
    """General test cases for Estimators."""

    def setUp(self):
        self.prod_config = load_config(environ="prod")
        self.dev_config = load_config(environ="dev")

    @parameterized.expand(list(League))
    def test_learner_exists_prod(self, league: League):
        """Ensure there is a serial model for each league in production."""
        estimator_cls_name = get_default_estimator(league=League)
        serial_model_name = f"{league.value}_{estimator_cls_name}.pkl"

        estimator_path = ESTIMATOR_LOCATION / "prod" / serial_model_name

        self.assertTrue(
            estimator_path.exists(),
            (
                f"Serialized Estimator ({serial_model_name}) not found for "
                f"{league} in env 'PROD'!"
            ),
        )

    @parameterized.expand(list(League))
    def test_learner_exists_dev(self, league: League):
        """Ensure there is a serial model for each league in development."""
        estimator_cls_name = get_default_estimator(league=League)
        serial_model_name = f"{league.value}_{estimator_cls_name}.pkl"

        estimator_path = ESTIMATOR_LOCATION / "dev" / serial_model_name

        self.assertTrue(
            estimator_path.exists(),
            (
                f"Serialized Estimator ({serial_model_name}) not found for "
                f"{league} in env 'DEV'!"
            ),
        )
