from sqlalchemy.orm.exc import NoResultFound
from flask import url_for, request, redirect, flash, render_template
from flask_login import current_user, logout_user, login_user
from . import auth
from .helpers import get_next_path
from .forms import LoginForm
from app.models import User


# @auth.route("/login", methods=["GET", "POST"])
# # @limiter.limit(settings.THROTTLE_LOGIN_PATTERN)
# def login():
#
#     index_url = url_for("main.index")
#     unsafe_next_path = request.args.get("next", index_url)
#     next_path = get_next_path(unsafe_next_path)
#     if current_user.is_authenticated:
#         return redirect(next_path)
#
#     form = LoginForm()
#     if request.method == "POST":
#         try:
#             user = User.get_by_username(request.form["username"])
#             if user and user.verify_password(request.form["password"]):
#                 # remember = "remember" in request.form
#                 login_user(user)
#                 return redirect(next_path)
#             else:
#                 flash("Wrong email or password.")
#         except NoResultFound:
#             flash("Wrong email or password.")
#
#     return render_template("auth/login.html", form=form,  next=next_path)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    user = User.query.first()
    if user == None:
        return redirect(url_for('routes.setup'))

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.password_hash is not None and \
                user.verify_password(form.password.data):
            login_user(user)
            flash('Welcome back ' + current_user.first_name + '!', 'success')
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('Wrong username or password.')

    return render_template('login.html', form=form)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
