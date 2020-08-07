from django.urls import path

from djaveAPI.views.ajax import ajax_get, ajax_update, ajax_delete
from djaveAPI.views.api import list_or_save_new, get_or_save_existing


djave_api_urls = [
    path('ajax_get', ajax_get, name='ajax_get'),
    path('ajax_update', ajax_update, name='ajax_update'),
    path('ajax_delete', ajax_delete, name='ajax_delete'),

    # These patterns capture quite a lot so they have to come last. They're for
    # the API.
    path('<model_name>', list_or_save_new, name='list_or_save_new'),
    path(
        '<model_name>/<pk>', get_or_save_existing,
        name='get_or_save_existing')]
