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

PROFILE_EXAMPLE = {
    u'client': u'Feedly sandbox client', u'created': 1401,
    u'dropboxConnected': False, u'email': u'example@example.com',
    u'evernoteConnected': False, u'facebookConnected': False,
    u'familyName': u'last name', u'fullName': u'First and Last name',
    u'gender': u'male', u'givenName': u'first name', u'google': u'23123',
    u'id': u'85e8-f77bba5600d0', u'paymentProviderId': {},
    u'paymentSubscriptionId': {},
    u'picture': u'https://lh5.example.com/dummy_picture.png',
    u'pocketConnected': False, u'twitterConnected': False, u'wave': u'2014.10',
    u'windowsLiveConnected': False, u'wordPressConnected': False
}

CATEGORIES_EXAMPLE = [{
    u'id': u'user/85e8-f77bba5600d0/category/Tech',
    u'label': u'Tech'
}, {
    u'id': u'user/85e8-f77bba5600d1/category/Cooking',
    u'label': u'Cooking'
}]

ENTRY_EXAMPLE = {
    "title": "NBC's reviled sci-fi drama 'Heroes'", "updated": 136753,
    "id": "_13fb9d6f274:2ac9c5:f5718180", "crawled": 136753,
    "tags": [{
        "id": "user/c805fcbf-3acf-4302-a97e-d82f9d7c897f/tag/global.saved"
    }, {
        "id": "user/c805fcbf-3acf-4302-a97e-d82f9d7c897f/tag/inspiration",
        "label": "inspiration"
    }],
    "alternate": [{
        "type": "text/html", "href": "http://theverge.com/4236096"
    }],
    "categories": [{
      "id": "user/c805fcbf-3acf-4302-a97e-d82f9d7c897f/category/tech",
      "label": "tech"
    }],
    "unread": True,
    "published": 1367568016,
    "author": "Nathan Ingraham",
    "content": {
        "direction": "ltr", "content": "..."
    },
    "origin": {
        "title": "The Verge -  All Posts", "htmlUrl": "http://www.theverge.com/",
        "streamId": "feed/http://www.theverge.com/rss/full.xml"
    },
    "engagementRate": 0.78,
    "canonical": [{
        "type": "text/html",
        "href": "http://www.theverge.com/2013/4/17/4236096/nbc-heroes-may-"
    }],
    "keywords": ["NBC", "sci-fi"],"engagement": 18
}