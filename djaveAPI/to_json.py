""" Turn an object into JSON suitable for publishing in an API. """
from djaveAPI.currency_field import corresponding_currency_field_name
from djaveAPI.find_models import use_model_instance_for_api
from djaveClassMagic.model_fields import model_fields, DATE_TIME, DATE
from djmoney.money import Money


TYPE = 'type'


def to_json_dict(instance, publishable_class=None):
  model, instance = use_model_instance_for_api(
      instance, publishable_class=publishable_class)

  as_dict = {TYPE: model.__name__}
  for field in model_fields(model):
    value = None
    if field.foreign_key_to:
      value = getattr(instance, '{}_id'.format(field.name))
    else:
      value = getattr(instance, field.name)
      if value is not None:
        if field.type in [DATE_TIME, DATE]:
          value = value.isoformat()
      if isinstance(value, Money):
        currency = value.currency.code
        value = float(value.amount)
        as_dict[corresponding_currency_field_name(field)] = currency
    as_dict[field.name] = value
  if hasattr(instance, 'add_to_json'):
    instance.add_to_json(as_dict)
  return as_dict
