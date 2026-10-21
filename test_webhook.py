import json
import hmac
import hashlib
import base64
import os
from dotenv import load_dotenv

# السطر ده هو الحل: بيقرا مفتاح التشفير من ملف .env
load_dotenv() 

from app import create_app
from app.models import db, Order

app = create_app()

def generate_hmac(payload_bytes, secret):
    digest = hmac.new(secret.encode('utf-8'), payload_bytes, hashlib.sha256).digest()
    return base64.b64encode(digest).decode('utf-8')

# بيانات الطلب الوهمي
payload_dict = {
    "id": 99887766,
    "phone": "01012345678",
    "customer": {"first_name": "أحمد"},
    "total_price": "1500.00",
    "currency": "EGP"
}
payload_bytes = json.dumps(payload_dict).encode('utf-8')

SECRET_KEY = "my_super_secret_hmac_key"
computed_hmac = generate_hmac(payload_bytes, SECRET_KEY)

headers = {
    "Content-Type": "application/json",
    "X-Shopify-Shop-Domain": "test-store.myshopify.com",
    "X-Shopify-Hmac-Sha256": computed_hmac
}

with app.test_client() as client:
    with app.app_context():
        print("\n--- 🚀 Test 1: First Webhook Request ---")
        response = client.post('/api/webhooks/shopify', data=payload_bytes, headers=headers)
        print(f"Response Status: {response.status_code}")
        print(f"Response Data: {response.get_json()}")
        
        print("\n--- 🔁 Test 2: Duplicate Request (Idempotency Test) ---")
        response2 = client.post('/api/webhooks/shopify', data=payload_bytes, headers=headers)
        print(f"Response Status: {response2.status_code}")
        print(f"Response Data: {response2.get_json()}")

        print("\n--- 🔒 Test 3: Database Security Check ---")
        order = Order.query.filter_by(shopify_order_id="99887766").first()
        if order:
            print(f"Order Status in DB: {order.status}")
            print(f"Raw Encrypted Phone in DB: {order._customer_phone}")
            print(f"Decrypted Phone via Model: {order.customer_phone}")
        print("\n=======================================\n")
