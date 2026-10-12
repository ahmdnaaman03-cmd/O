import os
import hmac
import hashlib
import base64
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from app.models import db, Order, Merchant

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

webhooks = Blueprint('webhooks', __name__)

# جلب المفتاح السري بأمان
SHOPIFY_SECRET = os.getenv('SHOPIFY_SECRET')

def verify_webhook(data, hmac_header):
    """دالة التحقق من صحة التوقيع الرقمي لشوبيفاي"""
    if not SHOPIFY_SECRET:
        print("❌ خطأ: المفتاح السري غير موجود في بيئة العمل.")
        return False
        
    digest = hmac.new(SHOPIFY_SECRET.encode('utf-8'), data, hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest).decode('utf-8')
    return hmac.compare_digest(computed_hmac, hmac_header)

@webhooks.route('/shopify', methods=['POST'])
def receive_shopify_order():
    try:
        request_data = request.get_data()
        hmac_header = request.headers.get('X-Shopify-Hmac-Sha256')

        if not hmac_header or not verify_webhook(request_data, hmac_header):
            print("❌ تنبيه أمني: محاولة وصول غير مصرح بها للـ Webhook")
            return jsonify({'error': 'Unauthorized'}), 401

        order_data = request.get_json()

        order_id_from_store = str(order_data.get('id', ''))
        total_price = order_data.get('total_price', '0.00')
        
        customer = order_data.get('customer', {})
        shipping = order_data.get('shipping_address', {})
        billing = order_data.get('billing_address', {})
        
        phone_number = (
            shipping.get('phone') or 
            customer.get('phone') or 
            billing.get('phone') or 
            order_data.get('phone')
        )
        
        customer_name = customer.get('first_name', '') + ' ' + customer.get('last_name', '')

        print(f"\n📥 استلام طلب جديد مؤكد من Shopify: {order_id_from_store}")
        print(f"📱 هاتف العميل: {phone_number}")

        merchant_id = 1 
        new_order = Order(
            order_id_from_store=order_id_from_store,
            customer_phone=phone_number,
            customer_name=customer_name.strip(),
            total_price=total_price,
            merchant_id=merchant_id,
            status='pending' if phone_number else 'manual_review'
        )
        
        db.session.add(new_order)
        db.session.commit()
        print(f"✅ تم حفظ الطلب بنجاح في قاعدة البيانات.")

        return jsonify({'message': 'Order processed', 'status': 'success'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ خطأ أثناء معالجة الطلب: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
