import json
from urllib import urlencode, quote_plus
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
        self.rate_limit_counter = 0

    def _make_request(self, method, endpoint, params={}, data={}, auth=True):
        """
        :param method: requests HTTP method to be used
        :param endpoint: url to be requested
        :param params: query string parameters
        :param data: json parameters (mostly for POST)
        :param auth: if request requires auth or not
        :return:
        """
        if auth and self.access_token is None:
            raise Exception("No access_token present")
        requests_method = getattr(requests, method)

        headers = {
            "Content-Type": "application/json"
        }
        if auth:
            # some API calls don't need authorization
            headers["Authorization"] = "OAuth {0}".format(self.access_token)

        response = requests_method(
            "{0}{1}".format(self.base_url, endpoint), params=params,
            data=json.dumps(data), headers=headers
        )
        if response.status_code != 200:
            raise Exception(
                "Got status code {response.status_code} and content "
                "{response.content}".format(**locals())
            )
        if "x-ratelimit-count" in response.headers:
            self.rate_limit_counter = response.headers["x-ratelimit-count"]
        return response.json()

    def _make_get_request(self, endpoint, **kwargs):
        """
        Makes a request to `endpoint` using available access_token.
        Throws Exception if access_token does not exist
        """
        return self._make_request("get", endpoint, **kwargs)

    def _make_post_request(self, endpoint, **kwargs):
        return self._make_request("post", endpoint, **kwargs)

    def _make_delete_request(self, endpoint, **kwargs):
        return self._make_request("delete", endpoint, **kwargs)

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
        return "{0}{1}?{2}".format(self.base_url, endpoint, query_string)

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
        credentials = self._make_post_request(
            endpoint, params=query_params, auth=False
        )
        if "access_token" not in credentials or "refresh_token" not in credentials:
            raise Exception("Authentication failed: {0}".format(credentials))
        self.access_token = credentials["access_token"]
        self.refresh_token = credentials["refresh_token"]
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
        credentials = self._make_post_request(
            endpoint, params=query_params, auth=False
        )
        if "access_token" in credentials:
            self.access_token = credentials["access_token"]
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
        self._make_post_request(
            "v3/categories/".format(quote_plus(category_id)),
            data={"label": label}
        )

    def delete_category(self, category_id):
        self._make_delete_request(
            "v3/categories/{0}".format(quote_plus(category_id))
        )

    # entries endpoints - http://developer.feedly.com/v3/entries
    def get_entry(self, entry_id, auth=True):
        return self._make_get_request(
            "v3/entry/{0}".format(quote_plus(entry_id)), auth=auth
        )

    def get_entry_list(self, entries, continuation=None, auth=True):
        """
        Get the content for a dynamic list of entries
        :param entries: list os entry ids (limited to 1000)
        """
        data = {
            "ids": entries
        }
        if continuation is not None:
            data["continuation"] = continuation
        return self._make_post_request("v3/entries/.mget", data=data)

    def create_and_tag_entry(self, entry):
        """
        Create and tag an entry
        The fields: title, content or summary or enclosure, alternate, published
        are mandatory
        Entry example at
        http://developer.feedly.com/v3/entries/#create-and-tag-an-entry
        """
        return self._make_post_request("v3/entries", data=entry)

    # feeds endpoints - http://developer.feedly.com/v3/feeds/
    def get_feed(self, feed_id):
        return self._make_get_request(
            "v3/feeds/{0}".format(quote_plus(feed_id))
        )

    def get_feed_list(self, feeds):
        """
        Get the metadata for a list of feeds
        :param feeds: list of feed ids
        """
        return self._make_post_request("v3/feeds/.mget", data=feeds)

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

    def undo_mark_as_read(self, category_ids=None, feed_ids=None):
        """
        Undo mark as read
        You can provide either `category_ids` or `feed_ids`. If you provide both
        only `category_ids` will be used.
        """
        if category_ids is None and feed_ids is None:
            raise Exception("you have to provide either feeds or categories")
        data = {
            "action": "undoMarkAsRead",
            "type": "categories"
        }
        if category_ids is not None:
            data["categoryIds"] = category_ids
        elif feed_ids is not None:
            data["feedIds"] = feed_ids
        return self._make_post_request("v3/markers/", data=data)

    def mark_articles_as_saved(self, entries):
        """
        Mark one or multiple articles as saved
        """
        data = {
            "entryIds": entries,
            "action": "markAsSaved",
            "type": "entries"
        }
        return self._make_post_request("v3/markers/", data=data)

    def mark_articles_as_unsaved(self, entries):
        """
        Mark one or multiple articles as unsaved
        """
        data = {
            "entryIds": entries,
            "action": "markAsUnsaved",
            "type": "entries"
        }
        return self._make_post_request("v3/markers/", data=data)

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

    # Mixes endpoints - http://developer.feedly.com/v3/mixes/
    def get_engaging_content(self, stream_id, auth=True, **kwargs):
        """
        Get a mix of the most engaging content available in a stream

        This API allows application to get access to the most engaging content
        available in a stream. The stream can be a feed, a category, or a topic.
        Allowed options:
            count - Optional integer number of entry ids to return. default is 3. max is 20.
            unread_only - Optional boolean default value is false.
            hours - Optional integer Hour of the day.
            newer_than - Optional long timestamp in ms.
            backfill - Optional boolean
            locale - Optional string preferred locale for results (used as a hint, not as a filter)
        Check http://developer.feedly.com/v3/mixes/ for more info
        """
        allowed_kwargs = [
            "count", "unread_only", "hours", "newer_than", "backfill", "locale"
        ]
        for key in kwargs:
            if key not in allowed_kwargs:
                raise Exception(
                    "Not valid key '{0}' provided as kwargs".format(key)
                )
        params = {
            "streamId": stream_id
        }
        params.update(kwargs)
        return self._make_get_request(
            "v3/mixes/contents", params=params, auth=auth
        )