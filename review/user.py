import logging
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user):
        logging.debug(f"User {user} logged in")
        self.user = user

    def has_general_approval_rights(self):
        return self.user["ris"]["has_general_approval_rights"]

    def ris_kuerzel(self):
        return self.user["ris"]["mitarb_kuerzel"]
