from django.shortcuts import reverse
from django.template.loader import render_to_string


def ajax_js():
  context = {
      'ajax_update_url': reverse('ajax_update'),
      'ajax_delete_url': reverse('ajax_delete')}
  return render_to_string('ajax.js', context)
