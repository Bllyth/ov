#
#
# from functools import wraps
# from flask import g, request, redirect, url_for
#
#
# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if g.user is None:
#             return redirect(url_for('login', next=request.url))
#         return f(*args, **kwargs)
#     return decorated_function
#
#
# def permission(name):
#     def inner(func):
#         func.__permission_name = name
#
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             if has_app_context() and role_check:
#
#
