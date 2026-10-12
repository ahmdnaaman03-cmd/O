from flask import Blueprint, request, jsonify
import os
import hmac
import hashlib
import base64

webhooks = Blueprint('webhooks', __name__)

SHOPIFY_SECRET = os.environ.get('SHOPIFY_SECRET', '')

def verify_webhook(data, hmac_header):
    if not SHOPIFY_SECRET:
        return False
    digest = hmac.new(SHOPIFY_SECRET.encode('utf-8'), data, hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest).decode('utf-8')
    return hmac.compare_digest(computed_hmac, hmac_header)

@webhooks.route('/shopify', methods=['POST'])
def handle_shopify_webhook():
    data = request.get_data()
    hmac_header = request.headers.get('X-Shopify-Hmac-Sha256')

    if not verify_webhook(data, hmac_header):
        print("❌ فشل التحقق من التوقيع!", flush=True)
        return jsonify({'error': 'Unauthorized'}), 401

    order_data = request.json
    print("✅ تم استلام الطلب والتحقق بنجاح!", flush=True)
    
    phone = (
        order_data.get('shipping_address', {}).get('phone') or
        order_data.get('customer', {}).get('phone') or
        order_data.get('billing_address', {}).get('phone') or
        order_data.get('phone')
    )
    
    print(f"📱 رقم الهاتف المستخرج: {phone}", flush=True)
    
    return jsonify({'status': 'success', 'message': 'Webhook received'}), 200
