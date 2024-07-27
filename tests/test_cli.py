import unittest

from click.testing import CliRunner

from entrypoints.cli import cli


class CliTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_predict_match_called_with_args(self):
        with unittest.mock.patch("entrypoints.cli.predict_match") as match:
            self.runner.invoke(
                cli,
                ["match", "--league", "EPL", "--home", "LIV", "--away", "ARS"],
            )
            match.assert_called_once_with(
                league="EPL", home_team="LIV", away_team="ARS", attendance=0.0
            )

    def test_predict_season_called_with_args(self):
        msg = "Sorry, I cannot predict seasons as yet!"
        with self.assertRaisesRegex(NotImplementedError, msg):
            result = self.runner.invoke(cli, "season --league EPL")
            if result:
                # We get back a result object instead of directly raising so
                # manually re-raising.
                raise result.exception
