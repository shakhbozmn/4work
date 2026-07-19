"""
Django settings package.
By default, loads development settings unless DJANGO_SETTINGS_MODULE is set.
"""

import os

# Determine which settings to use
settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "config.settings.development")

# Import the appropriate settings
if settings_module == "config.settings.production":
    from .production import *  # noqa: F401, F403
elif settings_module == "config.settings.development":
    from .development import *  # noqa: F401, F403
else:
    # Fallback to development
    from .development import *  # noqa: F401, F403
