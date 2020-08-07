from django.conf import settings


class CantUseNetwork(Exception):
  pass


def can_read_network(allowed_in_runserver=False):
  """ allowed_in_runserver is there because web tests on local and stage need
  to make network calls to fetch a guesty reservation, say. """
  # ALLOW_NETWORK_OVERRIDE is a global setting. It's terribly bad style to
  # change a global setting somewhere because that's how you get
  # non-deterministic behavior. So you should probably only ever change this
  # locally for some quick and dirty development. But in general, save yourself
  # a headache and don't use this.
  if settings.ALLOW_NETWORK_OVERRIDE:
    return True
  if settings.TEST:
    raise CantUseNetwork(
        'Tests should run fast and work offline, so you can\'t do network '
        'calls in tests.')
  elif settings.RUNSERVER and not allowed_in_runserver:
    raise CantUseNetwork(
        'Network calls are unpredictably slow and the website should always '
        'go fast. You should probably put this network call in a @background '
        'def.')
  return True


def can_write_network():
  if settings.ALLOW_NETWORK_OVERRIDE:
    return True
  can_read_network()
  if not settings.PROD:
    raise CantUseNetwork(
        'Only production is allowed to write over the network.')
  return True
