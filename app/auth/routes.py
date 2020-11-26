
from flask import redirect, render_template, url_for, flash, request
from flask_login import current_user, login_user, logout_user
from . import auth
from ..models import User
from .helpers import get_next_path
from app import db
from .forms import LoginForm


# @auth.before_request
# def before_request():
#     if current_user.is_authenticated:
#         current_user.ping()
#         return redirect(url_for('main.index'))


@auth.route('/', methods=['GET', 'POST'])
@auth.route('/login', methods=['GET', 'POST'])
def login():
    user = User.query.first()
    if user == None:
        flash('Please set up an account first', 'warning')
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

    return render_template('auth/login.html', form=form)


    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.get(form.username.data)
        if user:
            user.verify_password(form.password.data)
            user.authenticated = True
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("main.index"))

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()

    return redirect(url_for('auth.login'))





