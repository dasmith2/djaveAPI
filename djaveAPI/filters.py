from collections import namedtuple
from datetime import date

from django.utils.dateparse import parse_datetime, parse_date
from djaveAPI.paged_results import PAGE
from djaveClassMagic.model_fields import (
    model_fields, DATE_TIME, DATE, FLOAT, INTEGER)
from djaveAPI.problem import Problem
from djaveDT import to_tz_dt


def filter_model(model, api_key, request_GET):
  queryset = api_key.allowed_list(model)
  for _filter in get_filters(model, request_GET):
    field = _filter.filter_field
    if field.foreign_key_to:
      queryset = _filter_foreign_key(
          queryset, field, _filter.operator, _filter.value)
    else:
      key = field.name
      if _filter.operator:
        key = '{}__{}'.format(key, _filter.operator)
      queryset = queryset.filter(**{key: _parsed_value(field, _filter.value)})
  return queryset


AVAILABLE_OPERATORS = ['gt', 'gte', 'lt', 'lte']


Filter = namedtuple('Filter', 'filter_field operator value')


def get_filters(model, request_GET):
  _available_filters = available_filters(model)
  filters = []
  for key, value in request_GET.items():
    if key == PAGE or not value:
      continue
    field_name, operator = field_operator(key)
    if field_name not in _available_filters:
      raise Problem((
          '{} is not an available filter on {}. The available filters are '
          '{}').format(
          field_name, model.__name__, ', '.join(_available_filters.keys())))
    if operator and operator not in AVAILABLE_OPERATORS:
      raise Problem((
          'You tried to filter on {}, but {} is not an available operator. '
          'The available operators are {}').format(
              key, operator, ', '.join(AVAILABLE_OPERATORS)))
    filters.append(Filter(_available_filters[field_name], operator, value))
  return filters


def available_filters(model):
  to_return = {}
  for field in model_fields(model):
    if field.can_filter:
      to_return[field.name] = field
  return to_return


def _parsed_value(field, value):

  def _raise_problem():
    if field.type == DATE_TIME:
      example = to_tz_dt('2020-01-15 12:00').isoformat()
    elif field.type == DATE:
      example = date(2020, 1, 15).isoformat()
    elif field.type == FLOAT:
      example = '12.34'
    elif field.type == INTEGER:
      example = '123'
    else:
      raise Exception(
          'I dont know how to explain an example {}'.format(field.type))
    raise Problem((
        'Your {} filter is set to {}, which I was unable to parse. '
        'An example of something I can parse is '
        '{}').format(field.name, value, example))

  # As per Django's annoying habit, parse_date and parse_datetime swallow
  # errors and simply return None.
  to_return = None
  try:
    if field.type == DATE_TIME:
      to_return = parse_datetime(value)
    elif field.type == DATE:
      to_return = parse_date(value)
    elif field.type == FLOAT:
      to_return = float(value)
    elif field.type == INTEGER:
      to_return = int(value)
    else:
      raise Exception(
          'I dont know how to filter on type {}'.format(field.type))
  except ValueError:
    _raise_problem()
  if to_return is None:
    _raise_problem()
  return to_return


def _filter_foreign_key(queryset, field, operator, value):
  if operator:
    raise Problem((
        'When it comes to foreign key filters, I only support a single '
        'id like {}=12345. A range filter like {}__{} is invalid.').format(
            field.name, field.name, operator))
  if field.type != INTEGER:
    raise Exception('I dont know how to handle non-integer IDs yet')
  try:
    value = int(value)
  except ValueError:
    raise Problem((
        'The {} filter should be an integer. You specified: '
        '{}').format(field.name, value))
  return queryset.filter(**{field.name: value})


def field_operator(key):
  """ Given, like, submitted__gte, return ('submitted', 'gte') """
  if key.find('__') >= 0:
    return key.split('__')
  return (key, None)
