import unittest
from feedly import FeedlyAPI


class TestBaseFeedlyClass(unittest.TestCase):
    def setUp(self):
        self.feedly = FeedlyAPI(sandbox=True)
        self.test_code = (
            "AvYc7I97ImkiOiJkY2JlMTI1OS04Yjc2LTQ0NzEtODVlOC1mNzdiYmE1NjAwZDAi"
            "LCJ1IjoiMTA5ODMwNzc0ODI4MTgxMTQ1NTA0IiwiYSI6IkZlZWRseSBzYW5kYm94"
            "IGNsaWVudCIsInAiOjYsInQiOjE0MDYxOTg4NTQ1MDh9"
        )

    def test_get_auth_url(self):
        auth_url = (
            "https://sandbox.feedly.com/v3/auth/auth?scope=https%3A%2F%2Fcloud."
            "feedly.com%2Fsubscriptions&redirect_uri=http%3A%2F%2Flocalhost%3"
            "A8080%2F&response_type=code&client_id=sandbox"
        )
        f_auth_url = self.feedly.get_auth_url()
        self.assertEqual(auth_url, f_auth_url)