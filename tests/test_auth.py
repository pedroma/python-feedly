import unittest
import os
from feedly import FeedlyAPI


class TestBaseFeedlyClass(object):
    def test_auth(self):
        """
        Run this manually
        """
        client_id = os.environ.get('FEEDLY_CLIENT_ID')
        client_secret = os.environ.get('FEEDLY_CLIENT_SECRET')
        feedly = FeedlyAPI(
            client_id=client_id, client_secret=client_secret
        )
        auth_url = feedly.get_auth_url()
        print('Please authorize: ' + auth_url)
        code = raw_input('CODE: ').strip()
        credentials = feedly.get_access_token(code)
        # test a call
        feedly.get_profile()
