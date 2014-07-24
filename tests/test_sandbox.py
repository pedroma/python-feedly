import unittest
from feedly import FeedlyAPI


class TestBaseFeedlyClass(unittest.TestCase):
    def setUp(self):
        self.feedly = FeedlyAPI(sandbox=True)

    def test_get_auth_url(self):
        auth_url = (
            "https://sandbox.feedly.com/v3/auth/auth?scope=https%3A%2F%2Fcloud."
            "feedly.com%2Fsubscriptions&redirect_uri=http%3A%2F%2Flocalhost%3"
            "A8080%2F&response_type=code&client_id=sandbox"
        )
        f_auth_url = self.feedly.get_auth_url()
        self.assertEqual(auth_url, f_auth_url)

    def test_finish_authorization(self):
        self.feedly.finish_authorization("test_code")
        result = {
            u'errorCode': 400,
            u'errorMessage': u'expired or wrong code (check URL encoding)',
        }
        self.assertEqual(
            result["errorCode"], self.feedly.credentials["errorCode"]
        )
        self.assertEqual(
            result["errorMessage"], self.feedly.credentials["errorMessage"]
        )

    def test_refresh_token_exception(self):
        self.assertRaises(Exception, self.feedly.refresh_token())

    def test_refresh_token(self):
        self.feedly.credentials["refresh_token"] = "test_token"
        self.feedly.refresh_token()
        result = {
            u'errorCode': 401,
            u'errorMessage': u'bad refresh_token: test_token (check URL encoding)',
        }
        self.assertEqual(
            result["errorCode"], self.feedly.credentials["errorCode"]
        )
        self.assertEqual(
            result["errorMessage"], self.feedly.credentials["errorMessage"]
        )
