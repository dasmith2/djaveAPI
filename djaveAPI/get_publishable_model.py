from djaveAPI.find_models import publishable_model_from_name
from djaveAPI.problem import Problem


def get_publishable_model(model_name):
  model = publishable_model_from_name(model_name)
  if not model:
    raise Problem(
        'There is no {} API'.format(model_name), status_code=404)
  return model
