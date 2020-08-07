from datetime import date

from django.utils.dateparse import parse_datetime, parse_date
from djaveAPI.currency_field import corresponding_currency_value
from djaveAPI.get_publishable_model import get_publishable_model
from djaveAPI.problem import Problem
from djaveClassMagic.model_fields import (
    model_fields, DATE_TIME, DATE, FLOAT, INTEGER, TEXT, CHAR, BOOLEAN)
from djaveDT import now
from djmoney.money import Money


def update(instance, request_data, credentials):
  return _set_fields(instance, request_data, credentials)


def save_new(model, request_data, credentials):
  explain_why_not = credentials.explain_why_can_not_create(model)
  if explain_why_not:
    raise Problem(explain_why_not)
  return _set_fields(model(), request_data, credentials)


def _set_fields(instance, request_data, credentials):
  for field in model_fields(instance.__class__):
    if not field.editable:
      continue
    specified = field.name in request_data
    value = None

    if specified:
      raw_value = request_data[field.name]
      if field.foreign_key_to:
        if raw_value:
          # This line exists entirely because I need to use
          # djaveAPI.models.user.User when it's a foreign key to
          # django.contrib.auth.models.User
          check_credentials_against = get_publishable_model(
              field.foreign_key_to.__name__)

          value = credentials.allowed_list(check_credentials_against).filter(
              pk=raw_value).first()
          if value is None:
            raise Problem((
                'Either {} {} does not exist, or your API key does not have '
                'access to it').format(
                    field.foreign_key_to.__name__, raw_value))
          if not isinstance(value, field.foreign_key_to):
            raise Exception('value should be a {}, not {}'.format(
                field.foreign_key_to, value.__class__))
      elif field.type in [DATE, DATE_TIME]:
        value = _date_or_date_time(field, raw_value)
      elif field.type in [FLOAT, INTEGER]:
        value = _float_or_integer(field, raw_value)
        currency = corresponding_currency_value(field, request_data)
        if currency:
          value = Money(value, currency)
      elif field.type in [TEXT, CHAR]:
        if field.max_length and len(raw_value) > field.max_length:
          raise Problem((
              '{} has a maximum length of {}. You sent a string with '
              'length {}').format(
                  field.name, field.max_length, len(raw_value)))
        value = raw_value
      elif field.type == BOOLEAN:
        value = _boolean(field, raw_value)
      else:
        raise Exception(field.type)

    if field.required:
      required_error = False
      if specified:
        required_error = value in [None, '']
      else:
        required_error = getattr(instance, field.name) in [None, '']
      if required_error:
        raise Problem('"{}" is required'.format(field.display_name))

    if specified:
      setattr(instance, field.name, value)

  why_invalid = instance.explain_why_invalid()
  if why_invalid:
    raise Problem(why_invalid)
  instance.save()

  return instance


def _date_or_date_time(field, raw_value):
  if raw_value:
    if field.type == DATE:
      value = parse_date(raw_value)
      example = date.today().isoformat()
    elif field.type == DATE_TIME:
      value = parse_datetime(raw_value)
      example = now().isoformat()
    else:
      raise Exception(field.type)
    if not value:
      raise Problem((
          '{} is not a valid {}. I am looking for something more '
          'like {}').format(raw_value, field.type, example))
    return value


def _float_or_integer(field, raw_value):
  if raw_value not in ['', None]:
    try:
      if field.type == FLOAT:
        return float(raw_value)
      elif field.type == INTEGER:
        return int(raw_value)
      else:
        raise Exception(field.type)
    except ValueError:
      raise Problem(
          '{} is not a valid {}'.format(raw_value, field.type))


def _boolean(field, raw_value):
  if raw_value in ['', None]:
    return None
  return raw_value
