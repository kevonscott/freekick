import unittest

import numpy as np
import pandas as pd
from dateutil.parser import parse
from pandas.testing import assert_frame_equal

from freekick import DATA_DIR
from freekick.datastore.util import DataStore, EPLData, League


class DatastoreTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.epl_data = EPLData(datastore=DataStore.CSV, repository=None)

    def test_load_data(self):
        """Test freekick.model.load_data loads correct data."""
        league = League.EPL
        # data = load_data(d_location="CSV", league=league)
        data = self.epl_data.load()
        file_location = str(DATA_DIR / "processed" / f"{league.value}.csv")
        df = pd.read_csv(
            file_location, parse_dates=["Time"], date_format="mixed"
        )
        df["Date"] = df["Date"].apply(
            lambda d: parse(d) if isinstance(d, str) else np.nan
        )
        self.assertEqual(len(df), len(data))
