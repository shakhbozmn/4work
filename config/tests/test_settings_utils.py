"""Tests for the env helpers used by the production settings module."""

import os

from django.test import SimpleTestCase, override_settings

from config.settings.utils import (
    MissingSettingError,
    bool_env,
    csv_env,
    optional_env,
    required_env,
)


class RequiredEnvTest(SimpleTestCase):
    def test_returns_value_when_set(self):
        with override_settings():
            os.environ["FOO"] = "bar"
            try:
                self.assertEqual(required_env("FOO"), "bar")
            finally:
                del os.environ["FOO"]

    def test_raises_when_missing(self):
        with override_settings():
            os.environ.pop("FOO", None)
            with self.assertRaises(MissingSettingError):
                required_env("FOO")

    def test_raises_when_blank(self):
        with override_settings():
            os.environ["FOO"] = "   "
            try:
                with self.assertRaises(MissingSettingError):
                    required_env("FOO")
            finally:
                del os.environ["FOO"]


class CsvEnvTest(SimpleTestCase):
    def test_parses_comma_separated_values(self):
        with override_settings():
            os.environ["FOO"] = "a, b ,c"
            try:
                self.assertEqual(csv_env("FOO"), ["a", "b", "c"])
            finally:
                del os.environ["FOO"]

    def test_returns_empty_when_missing(self):
        with override_settings():
            os.environ.pop("FOO", None)
            self.assertEqual(csv_env("FOO"), [])


class BoolEnvTest(SimpleTestCase):
    def test_truthy_values(self):
        for raw in ("1", "true", "TRUE", "yes", "on"):
            with override_settings():
                os.environ["FOO"] = raw
                try:
                    self.assertTrue(bool_env("FOO"))
                finally:
                    del os.environ["FOO"]

    def test_default_when_missing(self):
        with override_settings():
            os.environ.pop("FOO", None)
            self.assertFalse(bool_env("FOO"))
            self.assertTrue(bool_env("FOO", default=True))


class OptionalEnvTest(SimpleTestCase):
    def test_returns_default(self):
        with override_settings():
            os.environ.pop("FOO", None)
            self.assertEqual(optional_env("FOO", default="x"), "x")
