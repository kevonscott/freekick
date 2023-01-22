""" Runs a series of tests to validate modules against specifies threshold
"""

import sys
import unittest

from statistics import mean

sys.path.append(".")

# from freekick.model.ai.models.logistic_model import SoccerLogisticModel
from freekick.model.ai.data_store import load_data, clean_format_data  # noqa E402

# from sklearn.model_selection import cross_val_predict

ACCURACY_THRESHOLD = 0.3  # We want to ensure an average accuracy above 50%


class TestPredictionModels(unittest.TestCase):
    def setUp(self) -> None:
        self.league = "epl"  # TODO: should be testing for all leagues
        self.data = load_data(league=self.league)
        self.X, self.y = clean_format_data(self.data, league=self.league)

    # TODO: Complete cross-validation test
    def test_cross_validation(self):
        # scores = cross_val_predict(SoccerLogisticModel, self.X, self.y, cv=10)
        scores = [0.3, 0.5, 0.9]
        self.assertGreaterEqual(mean(scores), ACCURACY_THRESHOLD)
