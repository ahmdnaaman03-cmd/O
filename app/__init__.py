from flask import Flask

def create_app():
    app = Flask(__name__)

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
