import functools

from flask_login import current_user
from flask import abort

view_only = True
not_view_only = False

ACCESS_TYPE_VIEW = "view"
ACCESS_TYPE_MODIFY = "modify"
ACCESS_TYPE_DELETE = "delete"

ACCESS_TYPES = (ACCESS_TYPE_VIEW, ACCESS_TYPE_MODIFY, ACCESS_TYPE_DELETE)


class require_permissions(object):
    def __init__(self, permissions, allow_one=False):
        self.permissions = permissions
        self.allow_one = allow_one

    def __call__(self, fn):
        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            if self.allow_one:
                has_permissions = any([current_user.has_permission(permission) for permission in self.permissions])
            else:
                has_permissions = current_user.has_permissions(self.permissions)

            if has_permissions:
                return fn(*args, **kwargs)
            else:
                abort(403)

        return decorated


def require_permission(permission):
    return require_permissions((permission,))


def require_admin(fn):
    return require_permission("admin")(fn)


def require_super_admin(fn):
    return require_permission("super_admin")(fn)
