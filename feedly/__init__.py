from urllib import urlencode
import requests


class FeedlyAPI(object):
    """
    Base class for the Feedly API. This class only implements the auth
    endpoints:
        * v3/auth/auth
        * v3/auth/token
    """
    # sandbox client id and client secret are temporary for development
    # get new one at: https://groups.google.com/forum/#!forum/feedly-cloud
    SANDBOX_CLIENT_ID = "sandbox"
    SANDBOX_CLIENT_SECRET = "ES3R6KCEG46BW9MYD332"
    SANDBOX_BASE_URL = "https://sandbox.feedly.com/"
    BASE_URL = "https://cloud.feedly.com/"

    def __init__(self, client_id=None, client_secret=None, sandbox=False, credentials={}):
        if sandbox:
            # allow client_id and client_secret overriding
            self.client_id = (
                client_id if client_id is not None else self.SANDBOX_CLIENT_ID
            )
            self.client_secret = (
                client_secret if client_secret is not None else self.SANDBOX_CLIENT_SECRET
            )
            self.base_url = self.SANDBOX_BASE_URL
        elif client_id is None or client_secret is None:
            raise Exception(
                "When using production environment "
                "client_id and client_secret must be provided"
            )
        else:
            self.client_id = client_id
            self.client_secret = client_secret
            self.base_url = self.BASE_URL
        # TODO: allow overriding of redirect_uri and scope
        self.redirect_uri = "http://localhost:8080/"
        self.scope = "https://cloud.feedly.com/subscriptions"
        self.credentials = credentials

    def _make_get_request(self, endpoint, params={}):
        """
        Makes a request to `endpoint` using available access_token.
        Throws Exception if access_token does not exist
        """
        if "access_token" not in self.credentials:
            raise Exception("No access_token present")
        response = requests.get(
            "".join([self.base_url, endpoint]), params=params,
            headers={
                "Authorization": "".join(["OAuth ", self.credentials["access_token"]])
            }
        )
        if response.status_code == 200:
            return response.json()

    def _make_post_request(self, endpoint, data={}):
        if "access_token" not in self.credentials:
            raise Exception("No access_token present")
        response = requests.post(
            "".join([self.base_url, endpoint]), data=data,
            headers={
                "Authorization": "".join(["OAuth ", self.credentials["access_token"]])
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
        self.credentials = response.json()
        return self.credentials

    def refresh_token(self):
        """
        Refresh existing access_token using refresh token
        """
        # check the existence of a refresh token
        if "refresh_token" not in self.credentials:
            raise Exception("Can't refresh token without a refresh_token value")
        endpoint = "v3/auth/token"
        query_params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.credentials["refresh_token"],
            "grant_type": "refresh_token"
        }
        request_url = "".join([self.base_url, endpoint])
        response = requests.post(request_url, params=query_params)
        self.credentials.update(response.json())
        return self.credentials

    # profiles endpoints - http://developer.feedly.com/v3/profile/
    def get_profile(self):
        """
        Returns a Profile dictionary
        """
        return self._make_get_request("v3/profile")

    def update_profile(self, fields={}):
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
        return self._make_post_request("v3/profile", fields=fields)

    # categories endpoints - http://developer.feedly.com/v3/categories/
    def get_categories(self):
        """
        Returns the user's categories
        """
        return self._make_get_request("v3/categories")

    def update_category(self, category_id):
        raise NotImplementedError("Not implemented yet")

    # entries endpoints - http://developer.feedly.com/v3/entries/#create-and-tag-an-entry
    def get_entry(self, entry_id):
        return self._make_get_request(
            "v3/entry/{entry_id}".format(entry_id)
        )