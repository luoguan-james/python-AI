# -*- coding: utf-8 -*-
"""
Test for settings module - verify LOG_LEVEL configuration can be imported.
"""

import pytest
import importlib
import sys


def test_log_level_exists():
    """Test that LOG_LEVEL is defined in settings."""
    # Remove any cached import
    if 'settings' in sys.modules:
        del sys.modules['settings']

    import settings
    assert hasattr(settings, 'LOG_LEVEL'), "LOG_LEVEL should be defined in settings"


def test_log_level_default_value():
    """Test that LOG_LEVEL has a reasonable default value."""
    if 'settings' in sys.modules:
        del sys.modules['settings']

    import settings
    assert settings.LOG_LEVEL in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'), \
        f"LOG_LEVEL={settings.LOG_LEVEL} is not a valid logging level"


def test_settings_importable():
    """Test that settings module can be imported without errors."""
    if 'settings' in sys.modules:
        del sys.modules['settings']

    # Should not raise any exception
    import settings
    assert settings.BOT_NAME == 'TS'
