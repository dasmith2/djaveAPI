from djaveAllowed.models import AllowedInterface
from djaveAPI.models.publishable_interface import PublishableInterface
from djaveAPI.signals import publishable_post_save


class PretendPublishable(AllowedInterface, PublishableInterface):
  def __init__(self, instance):
    self.instance = instance

  def __setattr__(self, name, value):
    if name in self.field_names():
      self.instance.__setattr__(name, value)
    else:
      super().__setattr__(name, value)

  def __getattr__(self, name):
    if name in self.field_names():
      return getattr(self.instance, name)
    return super().__getattr__(name)

  def field_names(self):
    return [f.name for f in self.__class__.get_model_fields()]

  def save(self):
    self.instance.save()
    publishable_post_save(sender=self.__class__, instance=self)

  def published_object(self):
    return self.instance

  @classmethod
  def get_model_fields(cls):
    raise NotImplementedError('get_model_fields {}'.format(cls))

  @classmethod
  def actually_publishing(cls):
    """ What actual model does this pretend class put in the API? """
    raise NotImplementedError('actually_publishing {}'.format(cls))
