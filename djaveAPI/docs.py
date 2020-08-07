from collections import namedtuple
from datetime import date
import json

from django.shortcuts import reverse
from django.template import loader
from djaveAPI.find_models import publishable_model_from_name
from djaveAPI.paged_results import construct_paged_results
from djaveAPI.to_json import TYPE
from djaveAPI.widgets.field_table import field_table
from djaveClassMagic.model_fields import (
    model_fields, DATE_TIME, DATE, INTEGER, FLOAT, TEXT, CHAR, BOOLEAN)
from djaveDT import to_tz_dt
from djaveURL import dict_as_query


def docs(model_name, api_root_url):
  model = publishable_model_from_name(model_name)
  template = loader.get_template('docs.html')
  model_description = None
  if hasattr(model, 'model_description'):
    model_description = model.model_description()
  else:
    model_description = 'Somebody go put def model_description() in {}'.format(
        model_name)
  # HAck! Fix this when I have a good example.
  model_plural_name = '{}s'.format(model_name)
  context = {
      'model_name': model_name,
      'model_name_lower': model_name.lower(),
      'model_plural_name': model_plural_name,
      'model_description': model_description,
      'fields_table': field_table(model),
      'examples': examples(model, api_root_url)}
  return template.render(context)


APIExample = namedtuple('APIExample', 'title code result')

GET_PREFIX = 'curl -u <api_key_username>:<api_key_password> {}'
POST_PREFIX = GET_PREFIX.format('-H "Content-Type: application/json" {}')


def examples(model, api_root_url):
  list_url = _base_url(api_root_url, model)
  filter_query_dict = example_filters(model)
  filter_query_dict['page'] = 1
  list_with_filters_url = '{}{}'.format(
      list_url, dict_as_query(filter_query_dict))
  get_one_url = '{}/{}'.format(list_url, 10)
  list_result = example_list_result(model)
  examples = [APIExample('Get all', GET_PREFIX.format(list_url), list_result)]
  examples.append(APIExample('Get a filtered list', GET_PREFIX.format(
      list_with_filters_url), list_result))
  single = example_single_result(model)
  examples.extend([
      APIExample('Get one', GET_PREFIX.format(get_one_url), single),
      APIExample('Create', example_create(model, api_root_url), single),
      APIExample('Update', example_update(model, api_root_url), single),
      APIExample(
          '"Delete"', example_delete(model, api_root_url),
          example_single_result(model, deleted=True)),
      APIExample('Webhook', example_webhook(model, single), '')])
  return examples


def example_webhook(model, single):
  return (
      '# If a new {} gets created, or an existing one changes,\n'
      '# and if you give your API Key a webhook URL, we will POST\n'
      '# something like this to your webhook URL:\n\n{}').format(
          model.__name__, single)


def example_list_result(model):
  as_dict = construct_paged_results([example_to_dict(model)], 1, 1, 1)
  return json.dumps(as_dict, indent=2)


def example_single_result(model, deleted=False):
  return json.dumps(example_to_dict(model, deleted=deleted), indent=2)


def example_to_dict(model, deleted=False):
  values = example_values(
      model, exclude=[], exclude_uneditable=False)
  values[TYPE] = model.__name__
  if 'deleted' in values and not deleted:
    values['deleted'] = None
  # This is for django's user
  if 'is_active' in values and deleted:
    values['is_active'] = False
  return values


def example_delete(model, api_root_url):
  the_rest = '-X DELETE {}/10'.format(_base_url(api_root_url, model))
  return GET_PREFIX.format(the_rest)


def example_create(model, api_root_url):
  values_str = example_values_str(
      model, exclude=['deleted'], exclude_uneditable=True)
  the_rest = '-d {} {}'.format(values_str, _base_url(api_root_url, model))
  return POST_PREFIX.format(the_rest)


def example_update(model, api_root_url):
  values_str = example_values_str(
      model, exclude=['deleted'], exclude_uneditable=True)
  the_rest = '-d {} {}/10'.format(values_str, _base_url(api_root_url, model))
  return POST_PREFIX.format(the_rest)


def _base_url(api_root_url, model):
  return '{}{}'.format(api_root_url, reverse(
      'list_or_save_new', kwargs={'model_name': model.__name__}))


def example_values(model, exclude=[], exclude_uneditable=True):
  values = {}
  for field in model_fields(model):
    if field.name in exclude:
      continue
    if exclude_uneditable and not field.editable:
      continue
    values[field.name] = _example_value(field)
  return values


def example_values_str(model, exclude=[], exclude_uneditable=True):
  values = example_values(model, exclude, exclude_uneditable)
  k_vs = []
  for key, value in values.items():
    # I read on StackOverflow from somebody using windows that single quotes
    # around JSON didn't work on the command line so they ended up escaping
    # double quotes.
    if isinstance(value, str):
      value = '\\"{}\\"'.format(value)
    k_vs.append('\\"{}\\": {}'.format(key, value))
  almost_there = '"{' + ', '.join(k_vs) + '}"'
  return almost_there.replace('True', 'true')


def example_filters(model):
  filters = {}
  for field in model_fields(model):
    if field.can_filter:
      name = field.name
      name__gte = '{}__gte'.format(name)
      name__lte = '{}__lte'.format(name)
      if field.foreign_key_to:
        filters[name] = _example_value(field)
      elif field.type == DATE_TIME:
        filters[name__gte] = _example_value(field)
        filters[name__lte] = to_tz_dt('2020-02-28 23:59').isoformat()
      elif field.type == DATE:
        filters[name__gte] = _example_value(field)
        filters[name__lte] = date(2020, 2, 28).isoformat()
      elif field.type == INTEGER:
        filters[name__gte] = _example_value(field)
        filters[name__lte] = 20
      elif field.type == FLOAT:
        filters[name__gte] = _example_value(field)
        filters[name__lte] = 200.2
      elif field.type == BOOLEAN:
        filters[name] = True
      else:
        raise Exception(
            'I am not sure what an example {} filter looks like'.format(
                field.type))
  return filters


def _example_value(field):
  if field.foreign_key_to:
    return 4321
  elif field.type == DATE_TIME:
    return to_tz_dt('2020-02-01 00:00').isoformat()
  elif field.type == DATE:
    return date(2020, 2, 1).isoformat()
  elif field.type == INTEGER:
    return 10
  elif field.type == FLOAT:
    return 100.1
  elif field.type in [TEXT, CHAR]:
    if field.name.find('_currency') > 0:
      return 'USD'
    return 'Hello'
  elif field.type == BOOLEAN:
    return True
  raise Exception(field.type)
