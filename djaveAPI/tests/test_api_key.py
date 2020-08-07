from django.contrib.auth.hashers import make_password
from djaveAPI.models.api_key import APIKey
from djaveTest.unit_test import TestCase, random_string


def set_api_key_stuff(api_key, **kwargs):
  api_key.username = kwargs.get('username', random_string())
  plain_password = kwargs.get('plain_password', None)
  hashed_password = kwargs.get('hashed_password', None)
  if plain_password and not hashed_password:
    hashed_password = make_password(plain_password)
  if not hashed_password:
    hashed_password = make_password('asdf1234')
  if plain_password:
    api_key.set_plain_password(plain_password)
  api_key.hashed_password = hashed_password
  api_key.webhook_url = kwargs.get('webhook_url', '')
  api_key.save()
  return api_key


class APIKeyTests(TestCase):
  def test_generate_and_use_key(self):
    key = APIKey.objects.create_key('Trailer park supervision')
    username = key.username
    plain_password = key.get_plain_password()

    self.assertEqual(key, APIKey.objects.get_api_key(username, plain_password))
    self.assertIsNone(APIKey.objects.get_api_key('wrong', plain_password))
    self.assertIsNone(APIKey.objects.get_api_key(username, 'wrong'))

    key.refresh_from_db()
    try:
      key.get_plain_password()
    except Exception:
      # You can only get the plain password immediately after you creating the
      # key because we only store hashed passwords in the database.
      pass
    self.assertEqual('Trailer park supervision', key.username)
