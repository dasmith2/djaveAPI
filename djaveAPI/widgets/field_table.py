from djaveClassMagic.model_fields import model_fields, TEXT, CHAR
from djaveTable.table import Table


def field_table(model):
  table = Table([
      'Field', 'Type', 'Description', 'Can filter', 'Required',
      'Not editable'])
  for field in model_fields(model):
    field_type = field.type
    if field_type == CHAR:
      field_type = '{}, max length {}'.format(TEXT, field.max_length)
    can_filter = '' if not field.can_filter else 'Filter'
    editable = '' if field.editable else 'Not editable'
    required = 'Required' if field.required and field.editable else ''
    help_text = ''
    if isinstance(field.help_text, str):
      # The User object has a field whose help_text is a
      # django.utils.functional.lazy.<locals>.__proxy__
      help_text = field.help_text

    table.create_row([
        field.name, field_type, help_text, can_filter,
        required, editable])
  return table
