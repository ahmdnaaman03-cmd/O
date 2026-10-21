import os
import hmac
import hashlib
import base64
import json
import re
from flask import Blueprint, request, jsonify
from app.models import db, Order, Merchant
from app.logger_setup import setup_logger
from app.messaging.whatsapp import send_whatsapp_confirmation

logger = setup_logger('orderping.webhooks')
webhooks = Blueprint('webhooks', __name__)

def verify_shopify_hmac(data: bytes, hmac_header: str, secret: str) -> bool:
    if not secret or not hmac_header:
        return False
    digest = hmac.new(secret.encode('utf-8'), data, hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest).decode('utf-8')
    return hmac.compare_digest(computed_hmac, hmac_header)

def normalize_phone(raw_phone: str) -> str:
    if not raw_phone: return ""
    cleaned = re.sub(r'[^\d+]', '', str(raw_phone).strip())
    if cleaned.startswith('00'): return '+' + cleaned[2:]
    if not cleaned.startswith('+'):
        return '+20' + cleaned[1:] if cleaned.startswith('0') else '+' + cleaned
    return cleaned

# ==========================================
# 1. Normal Orders Webhook (Uses Merchant Secret)
# ==========================================
@webhooks.route('/shopify', methods=['POST'])
def receive_shopify_order():
    shop_domain = request.headers.get('X-Shopify-Shop-Domain')
    if not shop_domain:
        return jsonify({"error": "Missing Shop Domain"}), 400

    merchant = Merchant.query.filter_by(store_url=shop_domain).first()
    if not merchant:
        return jsonify({"error": "Unauthorized Merchant"}), 401

    hmac_header = request.headers.get('X-Shopify-Hmac-Sha256')
    raw_data = request.get_data()
    
    # استخدام مفتاح التاجر
    if not verify_shopify_hmac(raw_data, hmac_header, merchant.webhook_secret):
        logger.error("Shopify HMAC verification failed")
        return jsonify({"error": "Invalid Signature"}), 401

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    shopify_order_id = str(data.get('id'))
    raw_phone = data.get('phone') or (data.get('customer') or {}).get('phone')
    customer_phone = normalize_phone(raw_phone)

    if not shopify_order_id or not customer_phone:
        return jsonify({"error": "Missing order_id or phone"}), 400

    existing_order = Order.get_by_merchant(merchant.id).filter_by(shopify_order_id=shopify_order_id).first()
    if existing_order:
        logger.info(f"Idempotency hit: Order {shopify_order_id} already exists.")
        return jsonify({"success": True, "message": "Already processed"}), 200

    try:
        new_order = Order(
            merchant_id=merchant.id,
            shopify_order_id=shopify_order_id,
            customer_phone=customer_phone,
            status='pending_whatsapp_sent'
        )
        db.session.add(new_order)
        db.session.commit()
        
        logger.info(f"Order {shopify_order_id} saved. Status: pending_whatsapp_sent.")

        customer_name = (data.get('customer') or {}).get('first_name', 'عميلنا العزيز')
        total_price = f"{data.get('total_price', '0.00')} {data.get('currency', 'EGP')}"
        send_whatsapp_confirmation(shopify_order_id, customer_name, customer_phone, total_price)

        return jsonify({"success": True}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# ==========================================
# 2. Shopify Mandatory GDPR Webhooks (Uses Global App Secret)
# ==========================================
@webhooks.route('/shopify/gdpr', methods=['POST'])
def shopify_gdpr_webhooks():
    shop_domain = request.headers.get('X-Shopify-Shop-Domain')
    topic = request.headers.get('X-Shopify-Topic')
    hmac_header = request.headers.get('X-Shopify-Hmac-Sha256')
    
    if not shop_domain or not topic:
        return jsonify({"error": "Missing Headers"}), 400

    # استخدام مفتاح التطبيق العام من البيئة
    GLOBAL_APP_SECRET = os.environ.get('SHOPIFY_APP_SECRET', '')
    raw_data = request.get_data()
    
    if not verify_shopify_hmac(raw_data, hmac_header, GLOBAL_APP_SECRET):
        logger.error(f"GDPR Webhook HMAC failed for {shop_domain}")
        return jsonify({"error": "Invalid Signature"}), 401

    merchant = Merchant.query.filter_by(store_url=shop_domain).first()
    if not merchant:
        return jsonify({"success": True}), 200 

    try:
        if topic == 'shop/redact':
            # التاجر مسح التطبيق: نمسح كل بياناته
            Order.query.filter_by(merchant_id=merchant.id).delete()
            db.session.delete(merchant)
            db.session.commit()
            logger.info(f"GDPR: Shop {shop_domain} uninstalled app. All data deleted.")

        return jsonify({"success": True}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"GDPR Webhook Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
