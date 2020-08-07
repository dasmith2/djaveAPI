from django.db import models
from djaveAllowed.models import Allowed
from djaveAPI.models.publishable_interface import PublishableInterface
from djaveAPI.signals import publishable_post_save
from djaveDT import now


class LivePublishableManager(models.Manager):
  def get_queryset(self):
    return self.model.filter_live(super().get_queryset())

  def allowed_by_user(self, user):
    return self.model.filter_allowed_by_user(user, self.get_queryset())


class Publishable(Allowed, PublishableInterface):
  """ Have your models inherit from this class if you want your models to be
  published online as part of a REST-ish API. """

  deleted = models.DateTimeField(blank=True, null=True, help_text=(
      'When was this object "deleted"? Deleted objects '
      'should basically be ignored.'))

  def delete(self):
    raise Exception(
        'If you actually delete a record and the consumer misses the '
        'webhook, how will they ever find out it was deleted? Use '
        'mark_deleted instead.')

  def destroy(self):
    return super().delete()

  def mark_deleted(self, nnow=None):
    nnow = nnow or now()
    self.deleted = nnow
    self.save()

  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    publishable_post_save.send(sender=self.__class__, instance=self)

  def published_object(self):
    return self

  @classmethod
  def filter_live(cls, query_set):
    return query_set.filter(deleted__isnull=True)

  live = LivePublishableManager()
  objects = models.Manager()

  class Meta:
    abstract = True
