import json
from urllib import urlencode
import requests
import os


class FeedlyAPI(object):
    """
    Base class for the Feedly API. This class only implements the auth
    endpoints:
        * v3/auth/auth
        * v3/auth/token

        Sandbox client_id: sandbox
        Sandbox client_secret: ES3R6KCEG46BW9MYD332
        These credentials will expire in 01/08/2014 get new ones at
        https://groups.google.com/forum/#!forum/feedly-cloud
    """
    SANDBOX_BASE_URL = "https://sandbox.feedly.com/"
    BASE_URL = "https://cloud.feedly.com/"

    def __init__(
            self, client_id=None, client_secret=None,
            access_token=None, refresh_token=None
    ):
        """
        There are 2 use cases for this class:
         * we already have an access token and a refresh token
         * we want to get an access token
        """
        client_keys_none = client_id is None or client_secret is None
        tokens_none = access_token is None or refresh_token is None
        if client_keys_none and tokens_none:
            raise Exception(
                "(client_id and client_secret) or "
                "(access_token and refresh_token) must be provided"
            )
        # allow client_id and client_secret overriding
        self.client_id = client_id
        self.client_secret = client_secret
        self.sandbox = False
        self.base_url = self.BASE_URL
        if self.client_id == "sandbox":
            self.base_url = self.SANDBOX_BASE_URL
            self.sandbox = True

        # TODO: allow overriding of redirect_uri and scope
        self.redirect_uri = "http://localhost:8080/"
        self.scope = "https://cloud.feedly.com/subscriptions"
        self.access_token = access_token
        self.refresh_token = refresh_token

    def _make_get_request(self, endpoint, params={}):
        """
        Makes a request to `endpoint` using available access_token.
        Throws Exception if access_token does not exist
        """
        if self.access_token is None:
            raise Exception("No access_token present")
        response = requests.get(
            "".join([self.base_url, endpoint]), params=params,
            headers={
                "Authorization": "".join(["OAuth ", self.access_token])
            }
        )
        if response.status_code == 200:
            return response.json()

    def _make_post_request(self, endpoint, data={}):
        if self.access_token is None:
            raise Exception("No access_token present")
        response = requests.post(
            "".join([self.base_url, endpoint]), data=json.dumps(data),
            headers={
                "Authorization": "".join(["OAuth ", self.access_token]),
                "Content-Type": "application/json"
            }
        )
        if response.status_code == 200:
            return response.json()

    def get_auth_url(self):
        """
        Get url the user should be sent to to get the code for authentication
        """
        endpoint = "v3/auth/auth"
        query_params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scope
        }
        query_string = urlencode(query_params)
        return "".join([self.base_url, endpoint, "?", query_string])

    def get_access_token(self, code):
        """
        Using code from redirect fetch valid credentails (access_token) for
        subsequent requests
        """
        endpoint = "v3/auth/token"
        query_params = {
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret

        }
        request_url = "".join([self.base_url, endpoint])
        response = requests.post(request_url, params=query_params)
        credentials = response.json()
        if "accessToken" not in credentials or "refreshToken" not in credentials:
            raise Exception("Authentication failed")
        self.access_token = credentials["accessToken"]
        self.refresh_token = credentials["refreshToken"]
        return credentials

    def update_access_token(self):
        """
        Refresh existing access_token using refresh token
        """
        # check the existence of a refresh token
        if self.refresh_token is None:
            raise Exception("Can't refresh token without a refresh_token value")
        endpoint = "v3/auth/token"
        query_params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"
        }
        request_url = "".join([self.base_url, endpoint])
        response = requests.post(request_url, params=query_params)
        credentials = response.json()
        if "accessToken" in credentials:
            self.access_token = credentials["accessToken"]
        return credentials

    # profiles endpoints - http://developer.feedly.com/v3/profile/
    def get_profile(self):
        """
        Returns a Profile dictionary
        """
        return self._make_get_request("v3/profile")

    def update_profile(self, **kwargs):
        """
        Fields allowed:
            email - Optional string
            givenName - Optional string
            familyName - Optional string
            picture - Optional string
            gender - Optional boolean
            locale - Optional string
            twitter - Optional string twitter handle. example: edwk
            facebook - Optional string facebook id
        """
        return self._make_post_request("v3/profile", data=kwargs)

    # categories endpoints - http://developer.feedly.com/v3/categories/
    def get_categories(self):
        """
        Returns the user's categories
        """
        return self._make_get_request("v3/categories")

    def update_category(self, category_id, label):
        """
        Change the label of an existing category
        """
        raise NotImplementedError("Not implemented yet")

    # entries endpoints - http://developer.feedly.com/v3/entries
    def get_entry(self, entry_id):
        return self._make_get_request("".join(["v3/entry/", entry_id]))

    def get_entry_list(self, entries):
        raise NotImplementedError("Not implemented yet")

    # feeds endpoints - http://developer.feedly.com/v3/feeds/
    def get_feed(self, feed_id):
        return self._make_get_request("".join(["v3/feeds/", feed_id]))

    def get_feed_list(self, feeds):
        raise NotImplementedError("Not implemented yet")

    # markers endpoints - http://developer.feedly.com/v3/markers/
    def get_unread_counts(self):
        return self._make_get_request("v3/markers/counts")

    def mark_articles_read(self, entries):
        """
        Mark one or multiple articles as read
        Entries is the list of entries to mark as read.
        """
        data = {
            "entryIds": entries,
            "action": "markAsRead",
            "type": "entries"
        }
        return self._make_post_request("v3/markers/", data=data)

    def keep_articles_unread(self, entries):
        """
        Keep one or multiple articles as unread
        """
        data = {
            "entryIds": entries,
            "action": "keepUnread",
            "type": "entries"
        }
        return self._make_post_request("v3/markers/", data=data)

    def mark_feed_as_read(self, feeds_id, last_read_entry=None, as_of=None):
        """
        Mark a feed as read
        :param feeds_id: list of feed identifiers
        :param last_read_entry: id of the last read entry on the feed
        :param as_of: UNIX timestamp (mark as read as_of)
        """
        data = {
            "action": "markAsRead",
            "type": "feeds",
            "feedIds": feeds_id,
        }
        if last_read_entry is not None:
            data["lastReadEntryId"] = last_read_entry
        elif as_of is not None:
            data["asOf"] = as_of
        else:
            raise Exception(
                "One of last_read_entry or as_of needs to be provided"
            )
        return self._make_post_request("v3/markers/", data=data)

    def mark_category_as_read(self, categories_ids, last_read_entry=None, as_of=None):
        """
        Mark a category as read
        """
        data = {
            "action": "markAsRead",
            "type": "categories",
            "categoryIds": categories_ids,
        }
        if last_read_entry is not None:
            data["lastReadEntryId"] = last_read_entry
        elif as_of is not None:
            data["asOf"] = as_of
        else:
            raise Exception(
                "One of last_read_entry or as_of needs to be provided"
            )
        return self._make_post_request("v3/markers/", data=data)

    def undo_mark_as_read(self):
        raise NotImplementedError("Not implemented yet")

    def mark_articles_as_saved(self):
        raise NotImplementedError("Not implemented yet")

    def mark_articles_as_unsaved(self):
        raise NotImplementedError("Not implemented yet")

    def get_latest_reads(self, newer_than=None):
        """
        Get the latest read operations (to sync local cache)
        :param newer_than: milliseconds, default is 30 days.
        """
        params = {}
        if newer_than is not None:
            params["newerThan"] = newer_than
        return self._make_get_request("v3/markers/reads", params=params)

    def get_latest_tagged_ids(self, newer_than=None):
        """
        Get the latest tagged entry ids
        :param newer_than: milliseconds, default is 30 days.
        """
        params = {}
        if newer_than is not None:
            params["newerThan"] = newer_than
        return self._make_get_request("v3/markers/tags", params=params)