import os
import requests
from app.logger_setup import setup_logger

logger = setup_logger('orderping.messaging')

def send_whatsapp_confirmation(order_id, customer_name, customer_phone, total_price):
    WHATSAPP_TOKEN = os.environ.get('WHATSAPP_TOKEN', '')
    PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')

    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        # استخدام الـ logger بدل print عشان فلتر الـ PII يشتغل ويخفي الرقم
        logger.info(f"[SIMULATION] WhatsApp Message sent to {customer_phone}")
        logger.info(f"Body: أهلاً {customer_name}، تم استلام طلبك {order_id} بقيمة {total_price}.")
        return True

    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": customer_phone.replace("+", ""),
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": f"أهلاً {customer_name}،\nتم استلام طلبك رقم {order_id} بقيمة {total_price}.\nيرجى تأكيد أو إلغاء الطلب:"
            },
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": f"confirm_{order_id}", "title": "تأكيد الطلب"}},
                    {"type": "reply", "reply": {"id": f"cancel_{order_id}", "title": "إلغاء الطلب"}}
                ]
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        logger.info(f"WhatsApp sent successfully to {customer_phone}")
        return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp to {customer_phone}: {e}")
        return False
