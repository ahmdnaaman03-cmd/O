from flask import Blueprint

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
def show_dashboard():
    return "Dashboard: OrderPing stats will be here"
