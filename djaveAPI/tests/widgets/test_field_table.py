from djaveTest.unit_test import TestCase
from djaveAPI.models.user_api_key import UserAPIKey
from djaveAPI.widgets.field_table import field_table


class FieldTableTests(TestCase):
  def test_display(self):
    html = field_table(UserAPIKey).as_html()
    self.assertTrue(html.find('user') > 0)
