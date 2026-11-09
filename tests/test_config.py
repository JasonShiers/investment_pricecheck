"""Tests for config."""
import io
from contextlib import redirect_stderr
from pathlib import Path
from unittest import TestCase

from investment_prices.config import Settings

ENV = {
    "HOLDINGS_PATH": "/data/holdings.csv",
    "PRICES_PATH": "/data/prices.csv",
}


class TestSettings(TestCase):
    """Tests for Settings."""

    def test_paths_come_from_environment(self) -> None:
        """Paths should be taken from environment when no args are given."""
        settings = Settings.from_args([], env=ENV)
        self.assertEqual(settings.holdings_path, Path("/data/holdings.csv"))
        self.assertEqual(settings.prices_path, Path("/data/prices.csv"))

    def test_cli_overrides_environment(self) -> None:
        """A CLI argument should take precedence over the environment."""
        settings = Settings.from_args(["--holdings", "/other/h.csv"], env=ENV)
        self.assertEqual(settings.holdings_path, Path("/other/h.csv"))
        self.assertEqual(settings.prices_path, Path("/data/prices.csv"))

    def test_cli_alone_is_enough(self) -> None:
        """CLI arguments should suffice when the environment is empty."""
        settings = Settings.from_args(
            ["--holdings", "h.csv", "--output", "p.csv"],
            env={},
        )
        self.assertEqual(settings.holdings_path, Path("h.csv"))
        self.assertEqual(settings.prices_path, Path("p.csv"))

    def test_missing_path_is_a_usage_error(self) -> None:
        """A path supplied by neither CLI nor env should exit with usage."""
        stderr = io.StringIO()
        with self.assertRaises(SystemExit), redirect_stderr(stderr):
            Settings.from_args([], env={})
        self.assertIn("--holdings", stderr.getvalue())

    def test_empty_environment_value_counts_as_missing(self) -> None:
        """An empty environment value should be treated as not set."""
        env = {"HOLDINGS_PATH": "", "PRICES_PATH": "/data/prices.csv"}
        with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
            Settings.from_args([], env=env)

    def test_tilde_is_expanded(self) -> None:
        """A leading ~ in a path should be expanded to the home directory."""
        env = {"HOLDINGS_PATH": "~/h.csv", "PRICES_PATH": "~/p.csv"}
        settings = Settings.from_args([], env=env)
        self.assertNotIn("~", str(settings.holdings_path))
        self.assertNotIn("~", str(settings.prices_path))
