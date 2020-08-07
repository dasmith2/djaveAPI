from django.contrib.auth.models import User as DjangoUser
from django.db import models
from djaveAPI.models.api_key import APIKey, APIKeyManager
from djaveAllowed.models import Allowed
from djaveAllowed.credentials import HasUserCredentialsInterface


class UserAPIKeyManager(APIKeyManager):
  def get_user(self, username, plain_password):
    api_key = self.get_api_key(username, plain_password)
    if api_key:
      return api_key.user

  def create_key(self, username, user):
    # I know this function looks redundant, but without it I ran into some
    # confusion about how, exactly, you create a UserAPIKey.
    return super().create_key(username, user=user)


class UserAPIKey(APIKey, HasUserCredentialsInterface, Allowed):
  user = models.ForeignKey(DjangoUser, on_delete=models.CASCADE)

  objects = UserAPIKeyManager()

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return query_set.filter(user=user)

  def explain_why_can_not_create(self, of_model):
    from djaveAPI.models.user import User as DjaveAPIUser
    if issubclass(of_model, (DjangoUser, DjaveAPIUser)):
      return (
          'User level API keys only have access to a single user. They are '
          'not powerful enough to create new users.')
