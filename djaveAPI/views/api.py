from djaveAPI.api_endpoint import api_endpoint
from djaveAPI.filters import filter_model, get_filters
from djaveAPI.models.pretend_publishable import PretendPublishable
from djaveAPI.paged_results import paged_results, get_page
from djaveAPI.get_instance import get_instance
from djaveAPI.get_publishable_model import get_publishable_model
from djaveAPI.get_posted_json import get_posted_json
from djaveAPI.problem import Problem
from djaveAPI.save import update, save_new
from djaveAPI.to_json import to_json_dict


@api_endpoint
def list_or_save_new(request, api_key, model_name):
  model = get_publishable_model(model_name)
  if request.method == 'GET':
    return paged_results(
        model, filter_model(model, api_key, request.GET),
        page=get_page(request.GET))
  elif request.method in ['POST', 'PUT']:
    data = get_posted_json(request)
    if 'id' in data:
      raise Problem(
          'When saving a new {}, you should not specify an id'.format(
              model_name))
    instance = save_new(model, data, api_key)
    return to_json_dict(instance, model)
  else:
    raise Problem((
        'This API endpoint is not sure what to do with the {} '
        'request method').format(request.method))


@api_endpoint
def get_or_save_existing(request, api_key, model_name, pk):
  model = get_publishable_model(model_name)

  filters = get_filters(model, request.GET)
  filter_field_names = [f.filter_field.name for f in filters]
  if filter_field_names:
    raise Problem((
        'When getting or saving a single {}, no filters are valid. You '
        'specified {}').format(model_name, ', '.join(filter_field_names)), 400)

  instance = get_instance(model_name, model.objects, pk, api_key)
  if request.method == 'POST':
    update(instance, get_posted_json(request), api_key)
  elif request.method == 'DELETE':
    instance.mark_deleted()
  return to_json_dict(instance, model)


def get_request_api_obj(model, pk, credentials):
  instance = None
  try:
    find_with_model = model
    if issubclass(model, PretendPublishable):
      find_with_model = model.actually_publishing()
    instance = credentials.allowed_list(find_with_model).filter(pk=pk).first()
    if issubclass(model, PretendPublishable):
      instance = model(instance)
  except ValueError as ex:
    # "Field 'id' expected a number but got 'a'."
    if ex.args[0].find('number'):
      raise Problem('{} is not a valid integer'.format(pk), 400)
  if not instance:
    raise Problem((
        'Either there is no {} with id {}, or your credentials '
        'do not have permission to access it.').format(
            model.__name__, pk), 404)
  return instance
