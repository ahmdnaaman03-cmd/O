import os
import requests
from app.logger_setup import setup_logger

logger = setup_logger('orderping.messaging')

def send_whatsapp_confirmation(order_id, customer_name, customer_phone, total_price):
    WHATSAPP_TOKEN = os.environ.get('WHATSAPP_TOKEN', '')
    PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')

    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        logger.info(f"[SIMULATION] WhatsApp Message sent to {customer_phone}")
        return True

    # تم تحديث الفيرجن هنا لـ v26.0
    url = f"https://graph.facebook.com/v26.0/{PHONE_NUMBER_ID}/messages"
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
        
        # السطرين دول هيطبعوا تفاصيل الخطأ من ميتا لو حصل
        if response.status_code != 200:
            logger.error(f"Meta API Error Details: {response.text}")
            
        response.raise_for_status()
        logger.info(f"WhatsApp sent successfully to {customer_phone}")
        return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp to {customer_phone}: {e}")
        return False
