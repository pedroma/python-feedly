class Profile(object):
    def __init__(self, feedly_api):
        self.feedly_api = feedly_api

    def get(self):
        return self.feedly_api._make_get_request("v3/profile")

    def update(self, fields={}):
        raise NotImplementedError("Not implemented yet")