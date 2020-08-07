from djaveAPI.models.user_api_key import UserAPIKey
from djaveAPI.widgets.api_keys_widget import APIKeysTable


class UserAPIKeysTable(APIKeysTable):
  def __init__(self, user, request_POST):
    self.user = user
    super().__init__(UserAPIKey, request_POST)

  def existing_keys(self):
    return UserAPIKey.objects.filter(user=self.user).order_by('-pk')

  def create_key(self, username):
    return UserAPIKey.objects.create_key(username, user=self.user)
