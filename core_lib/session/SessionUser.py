

class SessionUser(object):

    def __init__(self, id, facebook_id, token):
        self.id          = id
        self.facebook_id = facebook_id
        self.token       = token
