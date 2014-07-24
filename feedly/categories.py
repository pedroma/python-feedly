class Categories(object):
    def __init__(self, feedly_api):
        self.feedly_api = feedly_api

    def get(self):
        return self.feedly_api._make_get_request("v3/categories")

    def update(self, category_id):
        raise NotImplementedError("Not implemented yet")