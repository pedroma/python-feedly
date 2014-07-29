import json
import unittest
import os
from httmock import urlmatch, HTTMock, response
from feedly import FeedlyAPI
from tests.config import PROFILE_EXAMPLE, CATEGORIES_EXAMPLE, ENTRY_EXAMPLE


@urlmatch(netloc=r'(.*\.)?sandbox\.feedly\.com$', path="/v3/profile")
def get_profile_successfull(url, request):
    headers = {"x-ratelimit-count": 0}
    return response(200, json.dumps(PROFILE_EXAMPLE), headers)


@urlmatch(netloc=r'(.*\.)?sandbox\.feedly\.com$', path="/v3/profile")
def update_profile_successfull(url, request):
    headers = {"x-ratelimit-count": 0}
    profile = PROFILE_EXAMPLE.copy()
    profile.update(json.loads(request.body))
    return response(200, json.dumps(profile), headers)


@urlmatch(netloc=r'(.*\.)?sandbox\.feedly\.com$', path="/v3/categories")
def get_categories_successfull(url, request):
    headers = {"x-ratelimit-count": 0}
    return response(200, json.dumps(CATEGORIES_EXAMPLE), headers)


@urlmatch(netloc=r'(.*\.)?sandbox\.feedly\.com$', path="/v3/entry")
def get_entries_successfull(url, request):
    headers = {"x-ratelimit-count": 0}
    return response(200, json.dumps(ENTRY_EXAMPLE), headers)


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

    def test_get_profile(self):
        with HTTMock(get_profile_successfull):
            profile_response = self.feedly.get_profile()
        self.assertTrue("givenName" in profile_response)
        self.assertTrue("id" in profile_response)

    def test_update_profile(self):
        # get old name, set a new one and revert back
        with HTTMock(update_profile_successfull):
            profile = self.feedly.update_profile(givenName="first name2")
        self.assertEqual(profile["givenName"], "first name2")

    def test_get_categories(self):
        with HTTMock(get_categories_successfull):
            categories = self.feedly.get_categories()
        self.assertEqual(categories, CATEGORIES_EXAMPLE)

    def test_update_category(self):
        # updating a category returns nothing by feedly
        with HTTMock(get_categories_successfull):
            category = self.feedly.update_category("sample", "new_label")
        self.assertEqual(category, None)

    def test_get_entry(self):
        with HTTMock(get_entries_successfull):
            entry = self.feedly.get_entry("super_entry")
        # super_entry does not exist
        self.assertEqual(entry, ENTRY_EXAMPLE)
