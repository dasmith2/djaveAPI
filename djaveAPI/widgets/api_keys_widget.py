from django.template import loader
from djaveAPI.models.api_key import username_available
from djaveClassMagic.edit_list_table import EditListTable
from djaveForm.button import Button
from djaveForm.field import SlugField, URLField
from djaveForm.form import Form
from djaveTable.table import Cell


class APIKeysWidget(object):
  def __init__(self, request, new_api_key_table, title, description):
    self.request = request
    self.new_api_key_table = new_api_key_table
    self.title = title
    self.description = description

  def as_html(self):
    template = loader.get_template('api_keys_widget.html')
    context = {
        'new_api_key_table': self.new_api_key_table,
        'title': self.title,
        'description': self.description}
    return template.render(context, request=self.request)


class NewAPIKeyForm(Form):
  def __init__(self):
    self.username_field = SlugField('username', required=True)
    self.webhook_url_field = URLField('new_webhook_url', required=False)
    self.save_button = Button('Create', button_type='submit')
    super().__init__([
        self.username_field, self.webhook_url_field, self.save_button])

  def is_valid(self):
    super_is_valid = super().is_valid()
    if not super_is_valid:
      return super_is_valid
    can_username = username_available(self.username_field.get_value())
    if not can_username:
      self.username_field.set_invalid_reason('This username is in use already')
    return can_username


class APIKeysTable(EditListTable):
  def __init__(self, model, request_POST):
    headers = ['API Key username', 'API Key password', 'Webhook URL', '']
    super().__init__(model, headers, classes=['margin-top-half'])
    self.form = NewAPIKeyForm()
    keys = list(self.existing_keys())

    if request_POST and self.form.a_button_was_clicked(request_POST):
      self.form.set_form_data(request_POST)
      if self.form.is_valid():
        new_api_key = self.create_key(self.form.username_field.get_value())
        webhook_url = self.form.webhook_url_field.get_value()
        if webhook_url:
          new_api_key.webhook_url = webhook_url
          new_api_key.save()
        keys = [new_api_key] + keys
        self.form = NewAPIKeyForm()

    self.setup_top_row()
    self.setup_keys_rows(keys)

    self.setup_edit_ajax(['webhook_url'])
    self.setup_delete_ajax('.delete', 'Delete API Key?')

  def setup_top_row(self):
    self.create_row([
        self.form.username_field, '',
        self.form.webhook_url_field, self.form.save_button])

  def setup_keys_rows(self, keys):
    for key in keys:
      password = '(Hidden forever)'
      if key.has_plain_password():
        password = (
            'Write this down because you\'ll never see it again:<br><br>'
            '<b class="plain_password">{}</b>').format(
                key.get_plain_password())
      webhook_url_field = URLField(
          'webhook_url', required=False, default=key.webhook_url)
      username_cell = Cell(key.username, classes=['username_cell'])
      self.create_row([
          username_cell, password, webhook_url_field, Button('Delete')],
          pk=key.pk)

  def existing_keys(self):
    raise NotImplementedError('existing_keys')

  def create_key(self, username):
    raise NotImplementedError('existing_keys')
