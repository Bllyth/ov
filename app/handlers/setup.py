from flask import redirect, request, url_for, render_template, flash
from wtforms import PasswordField, StringField, validators, SubmitField, IntegerField
from wtforms.fields.html5 import EmailField
from flask_wtf import FlaskForm
from ..models import User
from app import db
from . import routes

from flask_login import login_user


class SetupForm(FlaskForm):
    first_name = StringField("First name", validators=[validators.InputRequired()])
    last_name = StringField("Last name", validators=[validators.InputRequired()])
    username = StringField("Username", validators=[validators.InputRequired()])
    email = EmailField("Email Address", validators=[validators.Email()])
    phone = IntegerField('Phone', validators=[validators.InputRequired()])
    password = PasswordField("Password")
    submit = SubmitField("Submit")


def create_user(first_name, last_name, username, email, password, phone):
    # admin_group = Group(
    #     name="admin",
    #     permissions=["admin", "super_admin"],
    #     type=Group.BUILTIN_GROUP,
    # )
    #
    # default_group = Group(
    #     name="default",
    #     permissions=Group.DEFAULT_PERMISSIONS,
    #     type=Group.BUILTIN_GROUP,
    # )
    #
    # db.session.add_all([admin_group, default_group])
    # db.session.commit()

    user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
        phone=phone
        # group_ids=[admin_group.id, default_group.id],
    )
    user.full_name = user.first_name + ' ' + user.last_name
    user.hash_password(password)

    db.session.add(user)
    db.session.commit()

    return user


@routes.route("/setup", methods=["GET", "POST"])
def setup():

    form = SetupForm()
    # form.newsletter.data = True
    # form.security_notifications.data = True

    if request.method == "POST" and form.validate():
        user = create_user(
            form.first_name.data, form.last_name.data, form.username.data, form.email.data, form.password.data,
            form.phone.data
        )

        # user = User(
        #     first_name=form.first_name.data,
        #     last_name=form.last_name.data,
        #     username=form.username.data,
        #     email=form.username.data
        # )
        user.full_name = user.first_name + ' ' + user.last_name
        # db.session.add(user)
        # db.session.commit()

        login_user(user)

        # # signup to newsletter if needed
        # if form.newsletter.data or form.security_notifications:
        #     subscribe.delay(form.data)
        flash('Admin user has been created', 'success')
        return redirect(url_for("main.index"))

    return render_template("setup.html", form=form)
