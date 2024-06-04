import unittest

import numpy as np
import pandas as pd
import pkg_resources
from dateutil.parser import parse
from pandas.testing import assert_frame_equal

from freekick import DATA_DIR
from freekick.model import League, load_data


class DatastoreTestCase(unittest.TestCase):
    def test_load_data(self):
        """Test freekick.model.load_data loads correct data."""
        league = League.EPL
        data = load_data(d_location="CSV", league=league)
        file_location = str(DATA_DIR / "processed" / f"{league.value}.csv")
        df = pd.read_csv(file_location, parse_dates=["Time"])
        df["Date"] = df["Date"].apply(
            lambda d: parse(d) if isinstance(d, str) else np.nan
        )
        assert_frame_equal(df, data)
