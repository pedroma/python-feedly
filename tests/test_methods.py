import unittest
import os
from feedly import FeedlyAPI


class TestBaseFeedlyClass(unittest.TestCase):
    def setUp(self):
        # make sure that when you are testing you use the sandbox environment
        # these tests change feedly values
        access_token = os.environ.get('FEEDLY_ACCESS_TOKEN')
        refresh_token = os.environ.get('FEEDLY_REFRESH_TOKEN')
        client_id = os.environ.get('FEEDLY_CLIENT_ID')
        client_secret = os.environ.get('FEEDLY_CLIENT_SECRET')
        self.feedly = FeedlyAPI(
            client_id=client_id, client_secret=client_secret,
            access_token=access_token, refresh_token=refresh_token
        )
        # let's refresh the token right away to test the function and
        # make sure we have a valid token
        self.feedly.update_access_token()

    def test_get_profile(self):
        profile_response = self.feedly.get_profile()
        self.assertTrue("givenName" in profile_response)
        self.assertTrue("id" in profile_response)

    def test_update_profile(self):
        self.feedly.update_profile(fields={"givenName": "epdro2"})

    def test_get_categories(self):
        pass