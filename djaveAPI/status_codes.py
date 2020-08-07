from json import loads


class ServerError(Exception):
  pass


def raise_if_server_error(response, url=None, sent_data=None):
  """ These happen when there's a hard server error and the requestor didn't
  necessarily do anything wrong. """
  if is_server_error(response):
    server_error = ServerError(
        response.status_code, response.content, url, sent_data)
    server_error.status_code = response.status_code
    server_error.content = response.content
    server_error.url = url
    raise server_error


class NotOkError(Exception):
  """ These happen when I send a request to somebody else's API and their API
  tells me I did it wrong. """
  def __init__(self, status_code, content, url, sent_data):
    self.status_code = status_code
    self.content = content
    self.url = url
    self.sent_data = sent_data
    super().__init__(status_code, content, url, sent_data)

  def json(self):
    return loads(self.content.decode('utf-8'))


def raise_if_not_ok(response, url=None, sent_data=None):
  raise_if_server_error(response, url=url, sent_data=sent_data)
  if not is_ok(response):
    raise NotOkError(
        status_code=response.status_code, content=response.content, url=url,
        sent_data=sent_data)


def is_server_error(response):
  # (bad gateway, error, timeout)
  return response.status_code in (500, 502, 503, 504)


def is_ok(response):
  # 204 No Content. "The server has successfully fulfilled the request and
  # there is no additional content to send in the response payload body."
  return response.ok or response.status_code == 204
