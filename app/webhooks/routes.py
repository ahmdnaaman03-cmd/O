from flask import Blueprint

webhooks = Blueprint('webhooks', __name__)

@webhooks.route('/')
def receive_order():
    return "Webhooks: Ready to receive orders"
