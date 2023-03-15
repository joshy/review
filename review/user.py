import logging
import os

from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user):
        logging.debug(f"User {user} logged in")
        self.user = user
        self.admin_users = os.getenv("ADMIN_USERS")

    def has_general_approval_rights(self):
        if self.ris_kuerzel() in self.admin_users:
            return True
        return self.user["ris"]["has_general_approval_rights"]

    def ris_kuerzel(self):
        return self.user["ris"]["mitarb_kuerzel"]

    def login_name(self):
        return self.user["query"]
