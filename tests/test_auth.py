import unittest
import os
from httmock import urlmatch, HTTMock
from feedly import FeedlyAPI


AUTH_URL_SANDBOX = (
    "https://sandbox.feedly.com/v3/auth/auth?scope=https%3A%2F%2Fcloud.feedly."
    "com%2Fsubscriptions&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2F&respons"
    "e_type=code&client_id=sandbox"
)

AUTH_URL_PRODUCTION = (
    "https://cloud.feedly.com/v3/auth/auth?scope=https%3A%2F%2Fcloud.feedly."
    "com%2Fsubscriptions&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2F&respons"
    "e_type=code&client_id=sandbox"
)

@urlmatch(
    netloc=r'(.*\.)?sandbox\.feedly\.com$', path="/v3/auth/token",
    method="post"
)
def get_access_token_successfull(url, request):
    return '{"accessToken": "dummy_token", "refreshToken": "dummy_token"}'

@urlmatch(
    netloc=r'(.*\.)?sandbox\.feedly\.com$', path="/v3/auth/token",
    method="post"
)
def get_access_token_exception(url, request):
    return '{"errorCode": "dummy_code", "errorMessage": "dummy_message"}'


class TestFeedlyAuth(unittest.TestCase):
    def test_successfull_auth(self):
        client_id = os.environ.get('FEEDLY_CLIENT_ID')
        client_secret = os.environ.get('FEEDLY_CLIENT_SECRET')
        feedly = FeedlyAPI(
            client_id=client_id, client_secret=client_secret
        )
        auth_url = feedly.get_auth_url()
        if feedly.sandbox:
            check_url = AUTH_URL_SANDBOX
        else:
            check_url = AUTH_URL_PRODUCTION
        self.assertEqual(
            auth_url, check_url
        )
        with HTTMock(get_access_token_successfull):
            feedly.get_access_token("dummy code")
        self.assertTrue(feedly.access_token is not None)
        self.assertTrue(feedly.refresh_token is not None)

    def test_failed_auth(self):
        client_id = os.environ.get('FEEDLY_CLIENT_ID')
        client_secret = os.environ.get('FEEDLY_CLIENT_SECRET')
        feedly = FeedlyAPI(
            client_id=client_id, client_secret=client_secret
        )
        auth_url = feedly.get_auth_url()
        if feedly.sandbox:
            check_url = AUTH_URL_SANDBOX
        else:
            check_url = AUTH_URL_PRODUCTION
        self.assertEqual(
            auth_url, check_url
        )
        with HTTMock(get_access_token_exception):
            with self.assertRaises(Exception):
                feedly.get_access_token("dummy code")
        self.assertTrue(feedly.access_token is None)
        self.assertTrue(feedly.refresh_token is None)
