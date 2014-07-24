from urllib import urlencode
import requests


class FeedlyAPI(object):
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

    def _get_request_context(self):
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

    def get_auth_url(self):
        """
        Get url the user should be sent to to get the code for authentication
        """
        query_params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scope
        }
        query_string = urlencode(query_params)
        return "{self.base_url}v3/auth/auth?{query_string}".format(**locals())

    def finish_authorization(self, code, client_secret=None):
        query_params = self._get_request_context()
        query_params.update({
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"

        })
        request_url = "{self.base_url}v3/auth/token".format(**locals())
        response = requests.post(request_url, params=query_params)
        self.credentials = response.json()
        return self.credentials

    def refresh_token(self):
        # check the existence of a refresh token
        if "refresh_token" not in self.credentials:
            raise Exception("Can't refresh token without a refresh_token value")
        query_params = self._get_request_context()
        query_params.update({
            "refresh_token": self.credentials["refresh_token"],
            "grant_type": "refresh_token"
        })
        request_url = "{self.base_url}v3/auth/token".format(**locals())
        response = requests.post(request_url, params=query_params)
        self.credentials.update(response.json())
        return self.credentials
