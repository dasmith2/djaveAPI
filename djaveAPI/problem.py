class Problem(Exception):
  def __init__(self, message, status_code=None):
    status_code = status_code or 200
    self.message = message
    self.status_code = status_code
    super().__init__(message, status_code)
