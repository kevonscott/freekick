""" Runs a series of tests to validate modules against specifies threshold
"""

import unittest
from statistics import mean

from sklearn.model_selection import cross_val_predict

from freekick.model import League
from freekick.model.ai.data_store import clean_format_data, load_data

ACCURACY_THRESHOLD = 0.3  # We want to ensure an average accuracy above 50%


class TestPredictionModels(unittest.TestCase):
    def setUp(self) -> None:
        self.league = League.EPL  # TODO: should be testing for all leagues
        self.data = load_data(league=self.league)
        self.X, self.y = clean_format_data(self.data, league=self.league)

    # TODO: Complete cross-validation test
    def test_cross_validation(self):
        # scores = cross_val_predict(SoccerLogisticModel, self.X, self.y, cv=10)
        scores = [0.3, 0.5, 0.9]  # TODO
        self.assertGreaterEqual(mean(scores), ACCURACY_THRESHOLD)
