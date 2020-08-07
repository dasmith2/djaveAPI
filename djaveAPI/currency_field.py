""" Money is a little tricky. In Django models I store it as a single Money
field. However, in the database that's a decimal field for the amount and a
char field for the currency. In the API, it's a float field for the amount and
a text field for the currency. """


def corresponding_currency_value(field, request_data):
  currency_field_name = corresponding_currency_field_name(field)
  if currency_field_name in request_data:
    return request_data[currency_field_name]


def corresponding_currency_field_name(field):
  return '{}_currency'.format(field.name)
