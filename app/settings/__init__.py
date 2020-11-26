import os
from .dynamic_settings import *
from .helpers import *


# Enforces CSRF token validation on API requests.
# This is turned off by default to avoid breaking any existing deployments but it is highly recommended to turn this toggle on to prevent CSRF attacks.
ENFORCE_CSRF = parse_boolean(
    os.environ.get("ENFORCE_CSRF", "true")
)

PAGE_SIZE = 5
