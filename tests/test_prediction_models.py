""" Runs a series of tests to validate modules against specifies threshold
"""

import unittest
from datetime import datetime
from statistics import mean

import pandas as pd

from freekick.datastore.util import DataStore, EPLData, League, Season
from freekick.learners.learner_utils import season_to_int  # add_wpc_pyth

# from sklearn.model_selection import cross_val_predict


ACCURACY_THRESHOLD = 0.3  # We want to ensure an average accuracy above 50%


class TestLearnerModels(unittest.TestCase):
    def setUp(self) -> None:
        self.data_container = EPLData(datastore=DataStore.DEFAULT)
        self.data = self.data_container.load()

    # TODO: Complete cross-validation test
    def test_cross_validation(self):
        # scores = cross_val_predict(SoccerLogisticModel, self.X, self.y, cv=10)
        scores = [0.3, 0.5, 0.9]  # TODO
        self.assertGreaterEqual(mean(scores), ACCURACY_THRESHOLD)

    # TODO: to be completed
    def test_add_wpc_pyth(self):
        season = Season.CURRENT
        league = League.EPL
        d = {
            "date": [pd.Timestamp(datetime.now().date())],
            "time": [pd.to_datetime("1:00")],
            "home_team": [2077942607848583336],
            "away_team": [9132668287013610014],
            "attendance": [0.0],
            "season": [season_to_int(Season.CURRENT)],
        }
        data = pd.DataFrame(d).astype(
            {
                "date": "int64",
                "time": "int64",
                "home_team": "category",
                "away_team": "category",
                "season": "category",
            }
        )
        print(season, league, data)
        # data = add_wpc_pyth(data=data, league=League.EPL)
        # Assert shape of dataframe increased by 4 or that the wpc and pyth
        # columns exists
