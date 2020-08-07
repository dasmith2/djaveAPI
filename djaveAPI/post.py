import requests
from djaveAPI.can_network import can_write_network


def post(url, data):
  """ This is a mock-able requests.post """
  if can_write_network():
    return requests.post(url, data=data).status_code == 200
