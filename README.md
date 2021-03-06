# Python feedly wrapper #
### I just started developing this so it doesn't have a lot of code for now. Should have something in a short while. ###

Sample usage:

    from feedly import FeedlyAPI
    feedly = FeedlyAPI(client_id="client_id", client_secret="client_secret")
    feedly.get_auth_url()
    'https://sandbox.feedly.com/v3/auth/auth?scope....'

At this point you have to go to the url given and login. After feedly redirects
you back (feedly's sandbox will always redirect you to `http://localhost:8080/`)
 you will have a code as a GET parameter

    code = "code_from_request"
    feedly.get_access_token(code)
   
At this point you will have a functional `FeedlyAPI` object. You can test 
some methods after this. For example:

    feedly.get_profile()
    
To be able to use the same token you have to store `feedly.access_token` and 
`feedly.refresh_token` to future use:

    feedly = FeedlyAPI(
        client_id="client_id", client_secret="client_secret", 
        access_token="access_token", refresh_token="refresh_token"
    )
    feedly.get_profile()


API endpoints checklist (http://developer.feedly.com/):

    [*] Authentication
    [*] Categories
    [*] Entries
    [ ] Evernote
    [ ] Facebook
    [*] Feeds
    [*] Markers
    [ ] Microsoft
    [*] Mixes
    [ ] OPML
    [ ] Preference
    [*] Profile
    [ ] Search
    [ ] Short URL
    [ ] Streams
    [ ] Subscriptions
    [ ] Tags
    [ ] Topics
    [ ] Twitter

`[*]` - Fully implemented
`[-]` - missing methods
`[ ]` - not implemented yet