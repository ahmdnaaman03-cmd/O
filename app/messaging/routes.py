import os
from flask import Blueprint, request, jsonify
from app.models import db, Order
from app.logger_setup import setup_logger
from app.shopify_api import add_tag_to_order

logger = setup_logger('orderping.messaging')
messaging = Blueprint('messaging', __name__)

@messaging.route('/whatsapp/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN', 'orderping_secure_token_123')
    
    if mode and token:
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            logger.info("WhatsApp Webhook verified successfully!")
            return challenge, 200
        return "Forbidden", 403
    return "OK", 200

@messaging.route('/whatsapp/webhook', methods=['POST'])
def receive_message():
    data = request.get_json()
    
    try:
        if data.get('object'):
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    if 'messages' in value:
                        message = value['messages'][0]
                        
                        if message.get('type') == 'interactive':
                            button_reply = message['interactive']['button_reply']
                            button_id = button_reply['id'] 
                            
                            action, order_id = button_id.split('_')
                            
                            order = Order.query.filter_by(shopify_order_id=order_id).first()
                            if order:
                                store_url = order.merchant.store_url
                                if action == 'confirm':
                                    order.status = 'confirmed'
                                    add_tag_to_order(store_url, order_id, '🟢 Confirmed')
                                    logger.info(f"Order {order_id} Confirmed by customer!")
                                elif action == 'cancel':
                                    order.status = 'cancelled'
                                    add_tag_to_order(store_url, order_id, '🔴 Cancelled')
                                    logger.info(f"Order {order_id} Cancelled by customer!")
                                
                                db.session.commit()
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}")
        
    return jsonify({"status": "success"}), 200
