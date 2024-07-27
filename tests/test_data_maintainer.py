import unittest
import unittest.mock

from click.testing import CliRunner
from parameterized import parameterized

from entrypoints.data_maintainer import cli
from freekick.datastore.util import League

LEAGUES = League._member_names_


class DataMaintainerTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_list_league(self):
        result = self.runner.invoke(cli, ["league", "--list"])
        self.assertEqual(result.stdout.strip(), "['EPL']")

    @parameterized.expand(LEAGUES)
    def test_update_player_rating_raises(self, league):
        pass
        with self.assertRaises(NotImplementedError):
            result = self.runner.invoke(
                cli,
                ["update", "--data-type", "player_rating", "--league", league],
            )
            raise result.exception

    @parameterized.expand(LEAGUES)
    def test_update_team_rating(self, league):
        with unittest.mock.patch(
            "freekick.datastore.util.DataScraper.scrape_team_rating"
        ) as scraper:
            self.runner.invoke(
                cli,
                ["update", "--data-type", "team_rating", "--league", league],
            )
            scraper.assert_called()

    @parameterized.expand(LEAGUES)
    def test_update_match_raises(self, league):
        with self.assertRaises(NotImplementedError):
            result = self.runner.invoke(
                cli, ["update", "--data-type", "match", "--league", league]
            )
            raise result.exception

    @parameterized.expand(LEAGUES)
    def test_update_current_season(self, league):
        with unittest.mock.patch(
            f"freekick.datastore.util.{league}Data.update_current_season"
        ) as updater:
            self.runner.invoke(
                cli,
                [
                    "update",
                    "--data-type",
                    "current_season",
                    "--league",
                    league,
                ],
            )
            updater.assert_called()
