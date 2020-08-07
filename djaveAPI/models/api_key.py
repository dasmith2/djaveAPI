""" By itself, an APIKey isn't much use. You're probably going to inherit from
APIKey in order to describe some kind of scope. djaveAPI.models.user_api_key is
an example. It's an API Key created at the user level.  """
from importlib import import_module
from secrets import token_urlsafe

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from djaveAllowed.credentials import CredentialsInterface
from djaveClassMagic.models.base_knows_child import BaseKnowsChild
from djaveForm.field import URLField


def api_key_types():
  types = []
  for type_str in settings.API_KEY_TYPES:
    parts = type_str.split('.')
    module_str = '.'.join(parts[:-1])
    class_str = parts[-1]
    module = import_module(module_str)
    types.append(getattr(module, class_str))
  return types


def username_available(username):
  return not APIKey.objects.filter(username=username).exists()


class APIKeyManager(models.Manager):
  def create_key(self, username, **kwargs):
    plain_password = token_urlsafe()
    hashed_password = make_password(plain_password)
    api_key = self.create(
        username=username, hashed_password=hashed_password, **kwargs)
    api_key.set_plain_password(plain_password)
    return api_key

  def get_api_key(self, username, plain_password):
    api_key = self.filter(username=username).first()
    if not api_key:
      return
    if check_password(plain_password, api_key.hashed_password):
      return api_key


class APIKey(BaseKnowsChild, CredentialsInterface):
  username = models.CharField(unique=True, max_length=100, help_text=(
      'Because passwords are encrypted in the database, we need a username '
      'to look up the key.'))

  # Actually this isn't really true. If a hacker gainst readonly access to the
  # database, they can read the django_session table which stores unencrypted
  # session keys. With a valid session key, a hacker can be logged in and just
  # go make a new APIKey.
  hashed_password = models.CharField(max_length=100, help_text=(
      'The password is salted and hashed. Then, if a hacker gains '
      'readonly access to the database, they will at least be prevented from '
      'immediately executing requests on behalf of teams.'))

  webhook_url = models.CharField(
      max_length=400, null=False, blank=True, default='', help_text=(
          'When any important object changes, what URL should we POST the new '
          'object data to?'))

  def __init__(self, *args, **kwargs):
    self._plain_password = None
    super().__init__(*args, **kwargs)

  def set_plain_password(self, plain_password):
    self._plain_password = plain_password

  def has_plain_password(self):
    return self._plain_password is not None

  def get_plain_password(self):
    if not self.has_plain_password():
      raise Exception(
          'You can only get the unhashed password immediately after '
          'creating the key. We purposefully dont store unhashed '
          'passwords.')
    return self._plain_password

  def explain_why_invalid(self):
    super_explain = super().explain_why_invalid()
    if super_explain:
      return super_explain
    url_field = URLField('webhook_url', required=False)
    url_field.set_value(self.webhook_url)
    return url_field.explain_why_not_valid()

  objects = APIKeyManager()
