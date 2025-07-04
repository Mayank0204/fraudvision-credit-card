import os
from flask import Flask
from flask_login import LoginManager
from app.db_models import db, User
from app.auth_routes import register_auth_routes
from app.main_routes import register_main_routes 

def create_app():
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    os.makedirs(instance_path, exist_ok=True)

    app = Flask(__name__, instance_path=instance_path)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'fraudapp.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    register_auth_routes(app)
    register_main_routes(app)

    with app.app_context():
        db_path = os.path.join(instance_path, 'fraudapp.db')
        if not os.path.exists(db_path):
            db.create_all()
            print("✅ Database created at", db_path)

    return app
