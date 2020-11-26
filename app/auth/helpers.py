

from urllib.parse import urlsplit, urlunsplit


def get_next_path(unsafe_next_path):
    if not unsafe_next_path:
        return ""

    # Preventing open redirection attacks
    parts = list(urlsplit(unsafe_next_path))
    parts[0] = ""  # clear scheme
    parts[1] = ""  # clear netloc
    safe_next_path = urlunsplit(parts)

    # If the original path was a URL, we might end up with an empty
    # safe url, which will redirect to the login page. Changing to
    # relative root to redirect to the app root after login.
    if not safe_next_path:
        safe_next_path = "./"

    return safe_next_path