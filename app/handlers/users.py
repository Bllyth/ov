
from ..models import User
from ..permissions import require_admin, require_permission


def get_users(self, disabled, pending, search_term):
    if disabled:
        users = User.all_disabled(self.current_org)
    else:
        users = User.all(self.current_org)

    if pending is not None:
        users = User.pending(users, pending)