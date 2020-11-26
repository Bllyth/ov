from flask import Flask
from flask import session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, user_logged_in
from flask_moment import Moment
from flask_toastr import Toastr
from config import Config
from flask_wtf.csrf import CSRFProtect, generate_csrf
from app import settings
from flask_login import current_user
from flask_mail import Mail
from redis import Redis
import rq

db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
login = LoginManager()
login.login_view = 'auth.login'
moment = Moment()
toastr = Toastr()
csrf = CSRFProtect()
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    login.init_app(app)
    moment.init_app(app)
    toastr.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    app.redis = Redis.from_url(Config.REDIS_URL)
    app.task_queue = rq.Queue('optifast-tasks', connection=app.redis)

    # user_logged_in.connect(log_user_logged_in)
    # login.request_loader(request_loader)

    from app.auth import auth as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import main as main_bp
    app.register_blueprint(main_bp)

    from app.handlers import routes as routes_bp
    app.register_blueprint(routes_bp)

    @app.template_filter('fdate')
    def format_datetime(value, format='%d.%m.%Y'):
        return value.strftime(format)

    @app.template_filter('datef')
    def format_datetime(value, format='%d %b %Y'):
        return value.strftime(format)

    @app.template_filter('ampm')
    def format_datetime(value, format='%d %b %Y %H:%M:%S %P'):
        return value.strftime(format)

    from babel.numbers import format_currency

    @app.template_filter('shilling')
    def shilling(value):
        return format_currency(value, 'KSH ', locale='en_US')

    @app.after_request
    def inject_csrf_token(response):
        response.set_cookie("csrf_token", generate_csrf())
        return response

    if settings.ENFORCE_CSRF:
        @app.before_request
        def check_csrf():
            if not current_user.is_authenticated or 'user_id' in session:
                csrf.protect()

    return app


from app import models
