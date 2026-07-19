"""Tests for the /health/ endpoint."""

import json
from unittest.mock import patch

from django.core.cache import cache
from django.test import RequestFactory, TestCase, override_settings

from config.views import HealthCheckView


class HealthCheckViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _request(self):
        return self.factory.get("/health/")

    def test_returns_200_when_db_and_cache_pass(self):
        with patch.object(HealthCheckView, "_check_db", return_value=True), patch.object(
            HealthCheckView, "_check_cache", return_value=True
        ):
            response = HealthCheckView.as_view()(self._request())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        body = json.loads(response.content)
        self.assertEqual(
            body,
            {"status": "ok", "service": "4work", "components": {"database": "ok", "cache": "ok"}},
        )

    def test_returns_503_when_db_fails(self):
        with patch.object(HealthCheckView, "_check_db", return_value=False), patch.object(
            HealthCheckView, "_check_cache", return_value=True
        ):
            response = HealthCheckView.as_view()(self._request())
        self.assertEqual(response.status_code, 503)
        body = json.loads(response.content)
        self.assertEqual(body["status"], "degraded")
        self.assertEqual(body["components"]["database"], "error")

    def test_returns_503_when_cache_fails(self):
        with patch.object(HealthCheckView, "_check_db", return_value=True), patch.object(
            HealthCheckView, "_check_cache", return_value=False
        ):
            response = HealthCheckView.as_view()(self._request())
        self.assertEqual(response.status_code, 503)
        body = json.loads(response.content)
        self.assertEqual(body["status"], "degraded")
        self.assertEqual(body["components"]["cache"], "error")


class HealthProbeIntegrationTest(TestCase):
    """End-to-end probes against the live test DB + locmem cache."""

    def setUp(self):
        self.factory = RequestFactory()
        cache.clear()

    def test_db_probe_passes(self):
        self.assertTrue(HealthCheckView._check_db())

    def test_cache_probe_passes(self):
        self.assertTrue(HealthCheckView._check_cache())

    def test_full_view_returns_200(self):
        with override_settings(DEBUG=True):
            response = HealthCheckView.as_view()(self.factory.get("/health/"))
        self.assertEqual(response.status_code, 200)
