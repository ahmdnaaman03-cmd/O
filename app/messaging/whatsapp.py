# -*- coding: utf-8 -*-
import requests
import os

def send_whatsapp_confirmation(shopify_order_id, customer_name, customer_phone, total_price, *args, **kwargs):
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    whatsapp_token = os.getenv("WHATSAPP_TOKEN", "")
    
    url = f"https://graph.facebook.com/v21.0/{phone_number_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json"
    }
    
    clean_phone = str(customer_phone).replace("+", "").strip()
    
    name_val = str(customer_name) if customer_name else "عميلنا العزيز"
    order_val = str(shopify_order_id) if shopify_order_id else "---"
    price_val = str(total_price) if total_price else "0"
    
    payload = {
        "messaging_product": "whatsapp",
        "to": clean_phone,
        "type": "template",
        "template": {
            "name": "order_confirm_auto_schedule",
            "language": {
                "code": "ar"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": name_val},
                        {"type": "text", "text": order_val},
                        {"type": "text", "text": price_val}
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "quick_reply",
                    "index": "0",
                    "parameters": [
                        {"type": "payload", "payload": f"confirm_{order_val}"}
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "quick_reply",
                    "index": "1",
                    "parameters": [
                        {"type": "payload", "payload": f"cancel_{order_val}"}
                    ]
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()
        print(f"WhatsApp API Status: {response.status_code}, Response: {res_data}")
        return res_data
    except Exception as e:
        print(f"Connection Exception: {str(e)}")
        return {"error": str(e)}

send_whatsapp_message = send_whatsapp_confirmation
