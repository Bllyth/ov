from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from passlib.apps import custom_app_context as pwd_context
from .mixins import TimestampMixin
from .base import key_type, primary_key, Column, GFKBase
from app import db, login
from .models import Task, Download


class UserGroup(db.Model):
    __tablename__ = 'user_group'
    id = primary_key("UserGroup")
    name = Column(db.String(64))


class UserGroupPermission(db.Model):
    __tablename__ = 'user_group_permission'
    id = primary_key("UserGroupPermission")
    permission = Column(db.String(64))
    group = Column(db.Integer, db.ForeignKey('user_group.id'))


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = 'user'
    id = primary_key("User")
    confirmed = Column(db.Boolean, default=False)
    first_name = Column(db.String(64), index=True)
    last_name = Column(db.String(64), index=True)
    full_name = Column(db.String(255), index=True)
    username = Column(db.String(64), index=True, unique=True)
    phone = Column(db.BigInteger, index=True, unique=True)
    email = Column(db.String(64), unique=True, index=True)
    password_hash = Column(db.String(128), nullable=True)
    id_passport = Column(db.String(128), index=True, unique=True, nullable=True)
    group = Column(db.Integer, db.ForeignKey('user_group.id'), nullable=True)

    clients = db.relationship('Client', backref='client_user', lazy='dynamic')
    payments = db.relationship('Payment', backref='payment_user', lazy='dynamic')
    tasks = db.relationship('Task', backref='user', lazy='dynamic')

    def fullname(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_id(self):
        return self.id

    # def can(self, permissions):
    #     return self.role is not None and \
    #            (self.role.permissions & permissions) == permissions

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        # return check_password_hash(self.password_hash, password)
        return self.password_hash and pwd_context.verify(password, self.password_hash)

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter(cls.email == email)

    @classmethod
    def find_by_username(cls, email):
        return cls.query.filter(cls.email == email)

    @classmethod
    def find_by_phone(cls, email):
        return cls.query.filter(cls.email == email)

    @classmethod
    def find_by_id(cls, email):
        return cls.query.filter(cls.email == email)

    def launch_task(self, name, description, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue('app.tasks.' + name, *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description, user=self)

        db.session.add(task)
        db.session.commit()
        self.add_download(status=2, task_id=rq_job.get_id())
        return task

    def add_download(self, status, task_id):
        d = Download(status=status, user_id=self.id, task_id=task_id)
        db.session.add(d)
        db.session.commit()
        return d

    def get_tasks_in_progress(self):
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, user=self,
                                    complete=False).first()

    def __repr__(self):
        return '<User \'%s\'>' % self.full_name()


# class Task(db.Model):
#     id = db.Column(db.String(36), primary_key=True)
#     name = db.Column(db.String(128), index=True)
#     description = db.Column(db.String(128))
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     complete = db.Column(db.Boolean, default=False)
#
#     def get_rq_job(self):
#         try:
#             rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
#         except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
#             return None
#         return rq_job
#
#     # def get_progress(self):
#     #     job = self.get_rq_job()
#     #     return job.meta.get('progress', 0) if job is not None else 100


class AnonymousUser(AnonymousUserMixin):
    def can(self, _):
        return False

    def is_admin(self):
        return False


login.anonymous_user = AnonymousUser


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
