from djaveTest.unit_test import TestCase, get_test_user
from djaveAPI.widgets.api_keys_widget import APIKeysWidget
from djaveAPI.widgets.user_api_keys_table import UserAPIKeysTable


class ApiKeysWidgetTests(TestCase):
  def test_display(self):
    user = get_test_user()
    table = UserAPIKeysTable(user, {})
    description = 'Blah blah blah.'
    api_keys_widget = APIKeysWidget(
        None, table, 'User API Keys', description)
    html = api_keys_widget.as_html()
    self.assertTrue(html.find('Blah blah blah.') > 0)
