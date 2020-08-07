"""
I needed some test models that would get installed in tests but not in
production. If you look in main/settings.py you'll see

if TEST:
  INSTALLED_APPS.append('djaveAPI.tests.apps.DjaveAPITestsConfig')

This apps file needs these magic strings in order to be able to create test
only migrations and have the models be available in tests.
"""
from django.apps import AppConfig


class DjaveAPITestsConfig(AppConfig):
  name = 'djaveAPI.tests'
  label = 'djaveAPITests'
