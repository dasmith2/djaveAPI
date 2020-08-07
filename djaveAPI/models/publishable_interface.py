class PublishableInterface(object):
  """ By Publishable I mean, it's possible to put this type in the API.
  PretendPublishable and Publishable need to be different base classes. """

  def allowed_api_keys(self, api_key_type):
    """ Return a list of api_keys that are allowed to see this particular
    instance. So if you were to call bobs_car.allowed_api_keys(OwnerAPIKey)
    you probably want it to return [bobs_api_key].

    Pretty much the entire point of this function is to look up who we should
    send webhooks to whenever we save a published object. """
    raise NotImplementedError('allowed_api_keys {}'.format(self.__class__))

  def mark_deleted(self, nnow=None):
    raise NotImplementedError('mark_deleted')

  def published_object(self):
    """ What is the actual, like, Django model object instance that this here
    instance is really refering too? In the case of Publishable, it's just
    itself. It's only more complicated with PretendPublishable. """
    raise NotImplementedError('published_object')
