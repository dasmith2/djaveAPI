import json

from djaveAPI.models.api_key import api_key_types
from djaveAPI.models.publishable import Publishable
from djaveAPI.models.pretend_publishable import PretendPublishable
from djaveAPI.post import post
from djaveAPI.signals import publishable_post_save
from djaveAPI.to_json import to_json_dict
from djaveClassMagic.models.rm_old import RmOld, RmOldManager
from djaveDT import now
from djaveThread.background_command import background_command
from django.core.exceptions import AppRegistryNotReady
try:
  from django.contrib.contenttypes.models import ContentType
except AppRegistryNotReady:
  raise Exception(
      'The last time this happened it was because I put '
      '`from djavError.log_error import log_error` in djavError.__init__')
from django.db import models
from django.dispatch import receiver


@background_command
def send_webhooks():
  Webhook.objects.send()


@receiver(publishable_post_save)
def create_webhooks(instance, **kwargs):
  Webhook.objects.create_webhooks(instance)


class WebhookManager(RmOldManager):
  def keep_for_days(self):
    return 1

  def create_webhooks(self, publishable):
    if not isinstance(publishable, (Publishable, PretendPublishable)):
      raise Exception(
          'You can only create webhooks for objects that inherit from '
          'Publishable or PretendPublishable')
    obj = publishable.published_object()
    obj_id = obj.pk
    obj_type = ContentType.objects.get_for_model(type(obj))
    payload = json.dumps(to_json_dict(publishable))

    for api_key_type in api_key_types():
      allowed_keys = publishable.allowed_api_keys(api_key_type)
      if allowed_keys is None:
        raise Exception((
            'Apparently I dont know how to check which {} have access to '
            'this {}').format(api_key_type, publishable.__class__))
      for api_key in allowed_keys:
        webhook_url = api_key.webhook_url
        if not webhook_url:
          continue
        # Let's say I just always send a webhook any time an object saves. Then
        # let's say the customer writes code that accepts any webhook, and
        # saves to their database. Then let's say the customer writes code
        # that, any time an object saves, saves to our API. Infinite loop. So
        # only send a webhook if the object actually changed since the last
        # webhook.
        latest = self.latest(obj_id, obj_type, webhook_url)
        if latest and latest.payload == payload:
          continue

        self.create(
            obj_id=obj_id, obj_type=obj_type, payload=payload,
            webhook_url=webhook_url)

  def latest(self, obj_id, obj_type, webhook_url):
    return self.filter(
        obj_id=obj_id, obj_type=obj_type, webhook_url=webhook_url).order_by(
            '-created').first()

  def send(self, _post=None, nnow=None):
    for webhook in self.filter(
        success_at__isnull=True, attempts__lt=3).order_by('created'):
      webhook.send(_post=_post, nnow=nnow)


class Webhook(RmOld):
  """ Each webhook is a json payload that should be POST-ed to a URL.

  Webhook is one word! """
  obj_id = models.IntegerField(editable=False, help_text=(
      'What object id is this webhook talking about?'))
  obj_type = models.ForeignKey(
      ContentType, editable=False, on_delete=models.PROTECT, help_text=(
          'What type of object is this webhook talking about?'))
  payload = models.TextField(help_text=(
      'The actual json that will be POST-ed to a server'))
  webhook_url = models.CharField(max_length=400, help_text=(
      'Where should we post payload to?'))
  last_send_attempt_at = models.DateTimeField(
      null=True, blank=True, help_text=(
          'When, if ever, did this webhook last attempt to post?'))
  attempts = models.PositiveIntegerField(default=0, help_text=(
      'How many times did this Webhook attempt to post?'))
  success_at = models.DateTimeField(
      null=True, blank=True, help_text=(
          'When, if ever, did this Webhook successfully go out?'))

  objects = WebhookManager()

  def send(self, _post=None, nnow=None):
    _post = _post or post
    nnow = nnow or now()
    if _post(self.webhook_url, json.loads(self.payload)):
      self.success_at = nnow
    self.last_send_attempt_at = nnow
    self.attempts += 1
    self.save()
