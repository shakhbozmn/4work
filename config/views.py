"""Health check view used by Docker, Nginx, and load balancers."""

import logging

from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.views import View

logger = logging.getLogger(__name__)

HEALTH_CACHE_KEY = "__health_check__"


class HealthCheckView(View):
    """Verify the database and cache are reachable before returning 200."""

    def get(self, request):
        db_ok = self._check_db()
        cache_ok = self._check_cache()
        ok = db_ok and cache_ok
        body = {
            "status": "ok" if ok else "degraded",
            "service": "4work",
            "components": {
                "database": "ok" if db_ok else "error",
                "cache": "ok" if cache_ok else "error",
            },
        }
        return JsonResponse(body, status=200 if ok else 503)

    @staticmethod
    def _check_db() -> bool:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return True
        except Exception:
            logger.exception("Health check database probe failed")
            return False

    @staticmethod
    def _check_cache() -> bool:
        try:
            cache.set(HEALTH_CACHE_KEY, "1", timeout=5)
            return cache.get(HEALTH_CACHE_KEY) == "1"
        except Exception:
            logger.exception("Health check cache probe failed")
            return False
