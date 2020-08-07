import json

from djaveAPI.problem import Problem


def get_posted_json(request):
  try:
    return json.loads(request.body)
  except json.decoder.JSONDecodeError:
    if request.POST:
      raise Problem(
          'Your post is not a valid JSON string. One way this '
          'can happen is if you do a regular HTML post. For instance, in '
          'Python, requests.post(url, data=data, auth=auth) will fail while '
          'requests.post(url, json=data, auth=auth) will work.')
    else:
      raise Problem('The request contained invalid JSON')
