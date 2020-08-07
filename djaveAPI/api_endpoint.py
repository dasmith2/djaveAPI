""" This is a decorator for views that handle API requests, as opposed to AJAX
requests. """
import base64

from djaveAPI.ajax_endpoint import ajax_endpoint
from djaveAPI.models.api_key import APIKey
from djaveAPI.response import problem_response
from djaveAPI.problem import Problem


class api_endpoint(ajax_endpoint):
  """ Unlike ajax_endpoint_login_required in djAveJax, which assumes requests
  are being sent by a logged in user, you'll use api_endpoint when requests are
  being sent by a server that's using API Keys. It adds a second argument to
  your view which is the API Key used to make the request, and turns off CSRF
  protection. """

  def __init__(self, request, *args, **kwargs):
    super().__init__(request, *args, **kwargs)
    self.csrf_exempt = True

  def __call__(self, request, *args, **kwargs):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
      return problem_response((
          'This API uses basic authentication, like doing '
          'curl -u api_key_username:api_key_password '
          'https://my-api'), status_code=401)
    weird_formatting_response = problem_response((
        'This API uses basic authentication. Server side, I am looking for '
        'a header titled "Authorization" with a value along the lines of '
        '"Basic dW5hbWU6cHdvcmQ=" where that dW5... string is a base 64 '
        'encoded string of your-username:your-password But probably you '
        'just want to use a library.'), status_code=401)
    if auth_header.find('Basic ') == -1:
      return weird_formatting_response
    auth_header = auth_header.replace('Basic ', '')
    uname_pword_str = base64.b64decode(auth_header).decode('utf-8')
    if uname_pword_str.find(':') == -1:
      return weird_formatting_response
    [username, plain_password] = uname_pword_str.split(':')
    if not username:
      return problem_response(
          'You did not include a username', status_code=401)
    if not plain_password:
      return problem_response(
          'You did not include a password', status_code=401)

    api_key = APIKey.objects.get_api_key(username, plain_password)
    if not api_key:
      return problem_response(
          'I do not recognize this username and password', status_code=401)
    try:
      return self.response_as_ajax(
          self.view_function(
              request, api_key.as_child_class(), *args, **kwargs))
    except Problem as ex:
      return problem_response(ex)
