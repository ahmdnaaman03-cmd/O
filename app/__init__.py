import os
from flask import Flask
from app.models import db

def create_app():
    app = Flask(__name__)
    
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, '..', 'orderping.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    with app.app_context():
        db.create_all()

    from app.webhooks.routes import webhooks
    from app.messaging.routes import messaging
    from app.dashboard.routes import dashboard
    from app.auth.routes import auth

    app.register_blueprint(webhooks, url_prefix='/api/webhooks')
    app.register_blueprint(messaging, url_prefix='/api/messaging')
    app.register_blueprint(dashboard, url_prefix='/dashboard')
    app.register_blueprint(auth, url_prefix='/auth')

    @app.route('/')
    def index():
        return "Welcome to OrderPing Core API!"

    return app
