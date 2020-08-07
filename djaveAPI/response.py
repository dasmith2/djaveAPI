from django.http import JsonResponse
from djaveAPI.problem import Problem


OK = {'OK': True}
OK_RESPONSE = JsonResponse(OK)


def problem_response(message_or_problem, status_code=None):
  """ message_or_problem can be a string or a Problem. If you pass in a
  Problem, you shouldn't also pass in a status_code because I'll get the
  status_code from the problem. """
  message = message_or_problem
  if isinstance(message_or_problem, Problem):
    message = message_or_problem.message
    if status_code:
      raise Exception(
          'Either pass in a string and a code, or pass in a Problem, but do '
          'not pass in a Problem and a code')
    status_code = message_or_problem.status_code
  else:
    status_code = 200
  return JsonResponse({'problem': message}, status=status_code)
