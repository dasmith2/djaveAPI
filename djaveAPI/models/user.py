""" Yeah, things got a little messy wiring Django's User class up to my
exquisite API. For starters, I needed a way to make the User email field unique
and make the email field indexed because I'm doing everything based on that
instead of username. I also copy the email field to the username field.

But then there's a bunch of magic, which I'm not super excited about. """
from django.contrib.auth.models import User as DjangoUser
from django.db import connection
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from djaveAPI.models.pretend_publishable import PretendPublishable
from djaveAPI.models.user_api_key import UserAPIKey
from djaveAPI.signals import publishable_post_save
from djaveRelease.signals import post_release


class User(PretendPublishable):
  """ Since I don't have control over Django's User class, I can't make it
  inherit from publishable. """
  def mark_deleted(self, nnow=None):
    self.instance.is_active = False
    self.instance.save()

  @classmethod
  def model_description(cls):
    return (
        'A User represents a human with an email address who uses the '
        'website.')

  @classmethod
  def get_model_fields(cls):
    model_fields = []
    for model_field in DjangoUser._meta.get_fields():
      if model_field.name in ['id', 'email', 'is_active']:
        model_fields.append(model_field)
    return model_fields

  @classmethod
  def actually_publishing(cls):
    return DjangoUser

  @classmethod
  def filter_live(cls, query_set):
    return query_set.filter(is_active=True)

  @classmethod
  def allowed_by_user(cls, user):
    return DjangoUser.objects.filter(pk=user.pk)

  def allowed_api_keys(self, api_key_type):
    if api_key_type is UserAPIKey:
      return UserAPIKey.objects.filter(user=self.instance)


@receiver(pre_save, sender=DjangoUser)
def pre_save_user(sender, instance, **kwargs):
  if instance.username != instance.email:
    instance.username = instance.email


@receiver(post_save, sender=DjangoUser)
def post_save_user(sender, instance, **kwargs):
  publishable_post_save.send(sender=User, instance=User(instance))


@receiver(post_release)
def post_release_user(*args, **kwargs):
  ensure_unique_email_index()


CREATE_UNIQUE_EMAIL_INDEX_SQL = (
    'CREATE UNIQUE INDEX auth_user_email ON auth_user USING btree (email);')
UNIQUE_EMAIL_INDEX_EXISTS_SQL = (
    "SELECT count(1) FROM pg_indexes WHERE tablename = 'auth_user' "
    "AND indexname = 'auth_user_email';")


def ensure_unique_email_index():
  if not unique_email_index_exists():
    create_unique_email_index()


def unique_email_index_exists():
  with connection.cursor() as cursor:
    cursor.execute(UNIQUE_EMAIL_INDEX_EXISTS_SQL)
    return cursor.fetchone()[0] == 1


def create_unique_email_index():
  with connection.cursor() as cursor:
    cursor.execute(CREATE_UNIQUE_EMAIL_INDEX_SQL)
