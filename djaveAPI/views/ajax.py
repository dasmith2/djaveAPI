from djaveAllowed.credentials import UserCredentials
from djaveAPI.ajax_endpoint import ajax_endpoint_login_required
from djaveAPI.get_request_variable import get_request_ajax_obj
from djaveAPI.problem import Problem
from djaveAPI.to_json import to_json_dict
from djaveAPI.save import update
from djaveClassMagic.model_fields import (
    model_fields_lookup, DATE_TIME, BOOLEAN)
from djaveDT import now


@ajax_endpoint_login_required
def ajax_get(request):
  return to_json_dict(get_request_ajax_obj(request))


@ajax_endpoint_login_required
def ajax_update(request):
  instance = get_request_ajax_obj(request)
  data = _js_variables_to_py(instance.__class__, request.POST)
  update(instance, data, UserCredentials(request.user))


def _js_variables_to_py(model, request_post):
  field_defs = model_fields_lookup(model)
  to_return = {}
  for key in request_post:
    if key not in ['pk', 'type', 'csrfmiddlewaretoken']:
      field = field_defs.get(key, None)
      if not field:
        raise Problem('{} is not a field in {}'.format(
            key, model.__class__.__name__))
      DATE_TIME
      if field.type == BOOLEAN and request_post[key] in [
          'true', 'false', 'True', 'False']:
        to_return[key] = request_post[key].lower() == 'true'
      elif field.type == DATE_TIME and request_post[key] in [
          'now', 'Now']:
        to_return[key] = now().isoformat()
      else:
        to_return[key] = request_post[key]
  return to_return


@ajax_endpoint_login_required
def ajax_delete(request):
  instance = get_request_ajax_obj(request)

  if hasattr(instance, 'deleted'):
    instance.deleted = now()
    instance.save()
  else:
    instance.delete()
