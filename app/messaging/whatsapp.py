# -*- coding: utf-8 -*-
import requests
import os

def send_whatsapp_message(customer_phone, order_id=None, total_price=None):
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "{PHONE_NUMBER_ID}")
    whatsapp_token = os.getenv("WHATSAPP_TOKEN", "{WHATSAPP_TOKEN}")
    
    url = f"https://graph.facebook.com/v26.0/{phone_number_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": customer_phone.replace("+", ""),
        "type": "template",
        "template": {
            "name": "order_confirm_auto_schedule",
            "language": {
                "code": "ar"
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()
        if response.status_code != 200:
            print(f"WhatsApp API Error: {res_data}")
        return res_data
    except Exception as e:
        print(f"Connection Exception: {str(e)}")
        return {"error": str(e)}
