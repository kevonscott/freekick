import unittest
import unittest.mock

from click.testing import CliRunner

from entrypoints.admin_cli import cli
from freekick.datastore.util import DataStore, League
from freekick.learners import DEFAULT_ESTIMATOR


class AdminCliTestcase(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_list_league_called(self):
        with unittest.mock.patch(
            "entrypoints.admin_cli.list_supported_leagues"
        ) as l_s_l:
            self.runner.invoke(cli, ["-l"])
            l_s_l.assert_called()

    def test_train_soccer_model_called_with_args(self):
        with unittest.mock.patch(
            "entrypoints.admin_cli.train_soccer_model"
        ) as t_s_m:
            self.runner.invoke(cli, ["-r", "EPL", "-s", "CSV"])
            t_s_m.assert_called_once_with(
                learner=DEFAULT_ESTIMATOR,
                league=League.EPL,
                test_size=0.2,
                datastore=DataStore.CSV,
                persist=False,
                repository=None,
            )
