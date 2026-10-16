import os
import re
import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify

logger = logging.getLogger('orderping.webhooks')

webhooks = Blueprint('webhooks', __name__)

def normalize_phone(raw_phone: str, default_country_code: str = "+20") -> str:
    if not raw_phone:
        return ""
    cleaned = re.sub(r'[^\d+]', '', str(raw_phone).strip())
    if cleaned.startswith('00'):
        cleaned = '+' + cleaned[2:]
    elif not cleaned.startswith('+'):
        if cleaned.startswith('0'):
            cleaned = default_country_code + cleaned[1:]
        else:
            cleaned = '+' + cleaned
    return cleaned

@webhooks.route('/orders/incoming', methods=['POST'])
@webhooks.route('/shopify', methods=['POST'])
@webhooks.route('/', methods=['POST'])
def receive_shopify_order():
    if not request.is_json:
        try:
            data = json.loads(request.get_data(as_text=True))
        except Exception:
            return jsonify({"success": False, "error": "INVALID_CONTENT_TYPE"}), 400
    else:
        data = request.get_json(silent=True)

    if not data or not isinstance(data, dict):
        return jsonify({"success": False, "error": "EMPTY_PAYLOAD"}), 400

    order_id = data.get('id') or data.get('order_id')
    order_name = data.get('name') or data.get('order_number') or f"#{order_id}"

    raw_phone = (
        data.get('phone') or
        (data.get('shipping_address') or {}).get('phone') or
        (data.get('billing_address') or {}).get('phone') or
        (data.get('customer') or {}).get('phone') or
        data.get('customer_phone')
    )

    if not order_id or not raw_phone:
        return jsonify({
            "success": False,
            "error": "MISSING_REQUIRED_FIELDS",
            "message": "Both order_id and customer_phone are required"
        }), 400

    customer_phone = normalize_phone(raw_phone)
    if len(customer_phone) < 8:
        return jsonify({
            "success": False,
            "error": "INVALID_PHONE_NUMBER",
            "message": f"Phone '{raw_phone}' is invalid"
        }), 400

    customer_name = (
        (data.get('customer') or {}).get('first_name') or
        (data.get('shipping_address') or {}).get('first_name') or
        data.get('customer_name') or
        "عميلنا العزيز"
    )
    total_price = str(data.get('total_price') or data.get('total_amount') or "0.00")
    currency = str(data.get('currency') or "EGP")

    return jsonify({
        "success": True,
        "message": "Order verified successfully",
        "order": {
            "order_id": str(order_id),
            "order_name": str(order_name),
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "total_price": total_price,
            "currency": currency
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200

@webhooks.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "online", "service": "OrderPing Webhooks"}), 200
