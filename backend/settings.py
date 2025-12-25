"""
Legacy settings file for backward compatibility.

This file now imports from the new settings structure.
For new code, use:
- backend.settings.development (for local development)
- backend.settings.production (for production)

This file defaults to development settings.
"""
import os

# Import development settings by default
# You can override by setting DJANGO_SETTINGS_MODULE environment variable
from .settings.development import *
