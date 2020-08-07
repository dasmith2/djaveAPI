from django.http import JsonResponse
from djaveAPI.problem import Problem
from djaveAPI.response import problem_response, OK_RESPONSE


class ajax_endpoint(object):
  """ A decorator for views that will return
  JsonResponse({'problem': 'Things bad!'}) when the view
  raises Problem('Things bad!') If the view returns data, return
  JsonResponse(data). If the view returns a JsonResponse, simply return the
  JsonResponse. If the view returns nothing, return, like,
  JsonResponse({'OK': True}, status_code=200) """
  def __init__(self, view_function):
    self.view_function = view_function

  def __call__(self, request, *args, **kwargs):
    try:
      return self.response_as_ajax(
          self.view_function(request, *args, **kwargs))
    except Problem as ex:
      return problem_response(ex)

  def response_as_ajax(self, response):
    if isinstance(response, JsonResponse):
      return response
    elif response is None:
      return OK_RESPONSE
    return JsonResponse(response)


class ajax_endpoint_login_required(ajax_endpoint):
  """ You'll use this to decorate functions that respond to user button clicks
  and such. """
  def __call__(self, request, *args, **kwargs):
    if request.user.is_authenticated:
      return super().__call__(request, *args, **kwargs)
    return problem_response('You are not logged in', 403)
