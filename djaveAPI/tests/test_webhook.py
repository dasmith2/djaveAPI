from unittest.mock import Mock

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from djaveAPI.models.webhook import Webhook
from djaveAPI.post import post
from djaveAPI.tests.models import MyFakeModel, get_test_my_fake_model
from djaveAPI.tests.test_user_api_key import get_test_user_api_key
from djaveDT import to_tz_dt
from djaveTest.unit_test import get_test_user, TestCase


class PublishableTests(TestCase):
  def setUp(self):
    super().setUp()
    self.user = get_test_user()
    get_test_user_api_key(user=self.user, webhook_url='https://test')

    # Irrelevant. Other user.
    get_test_user_api_key(user=get_test_user(), webhook_url='https://blargh')
    self.assertEqual(0, Webhook.objects.count())

  def test_create_webhooks(self):
    obj = get_test_my_fake_model(user=self.user)
    for i in range(2):
      obj.save()

    obj_type = ContentType.objects.get_for_model(MyFakeModel)

    self.assertEqual(1, Webhook.objects.count())
    webhook = Webhook.objects.get(
        obj_id=obj.pk, obj_type=obj_type, webhook_url='https://test',
        last_send_attempt_at=None, attempts=0, success_at=None)
    self.assertTrue(webhook.payload.find('Testname') > 0)

    obj.name = 'Tarstneme'
    for i in range(3):
      obj.save()
    self.assertEqual(2, Webhook.objects.count())
    next_webhook = Webhook.objects.get(
        ~Q(pk=webhook.pk),
        obj_id=obj.pk, obj_type=obj_type, webhook_url='https://test',
        last_send_attempt_at=None, attempts=0, success_at=None)
    self.assertTrue(next_webhook.payload.find('Tarstneme') > 0)

  def test_send(self):
    get_test_my_fake_model(user=self.user)

    _post = Mock(spec=post)
    _post.returnValue = True
    Webhook.objects.send(_post=_post, nnow=to_tz_dt('2020-01-15 12:00'))

    self.assertEqual(1, Webhook.objects.count())
    self.assertEqual(1, Webhook.objects.filter(
        last_send_attempt_at=to_tz_dt('2020-01-15 12:00'),
        attempts=1,
        success_at=to_tz_dt('2020-01-15 12:00')).count())


class PretendPublishableTests(TestCase):
  def setUp(self):
    super().setUp()
    self.user = get_test_user()
    get_test_user_api_key(user=self.user, webhook_url='https://test')
    get_test_user_api_key(user=get_test_user(), webhook_url='https://blargh')
    self.assertEqual(0, Webhook.objects.count())

  def test_create_webhooks(self):
    self.user.is_active = False
    self.user.save()
    self.assertEqual(1, Webhook.objects.count())
    obj_type = ContentType.objects.get_for_model(User)
    Webhook.objects.get(
        obj_id=self.user.pk, obj_type=obj_type, webhook_url='https://test',
        last_send_attempt_at=None, attempts=0, success_at=None)
