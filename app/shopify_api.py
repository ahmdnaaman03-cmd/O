import os
import requests
from app.logger_setup import setup_logger

logger = setup_logger('orderping.shopify_api')

def add_tag_to_order(store_url, order_id, tag):
    token = os.environ.get('SHOPIFY_ADMIN_TOKEN')
    if not token:
        logger.error("SHOPIFY_ADMIN_TOKEN is missing in .env")
        return False

    url = f"https://{store_url}/admin/api/2024-01/orders/{order_id}.json"
    headers = {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    }
    
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            existing_tags = resp.json().get('order', {}).get('tags', '')
            new_tags = f"{existing_tags}, {tag}" if existing_tags else tag
            
            payload = {"order": {"id": order_id, "tags": new_tags}}
            put_resp = requests.put(url, headers=headers, json=payload)
            
            if put_resp.status_code == 200:
                logger.info(f"Successfully added tag '{tag}' to order {order_id}")
                return True
            else:
                logger.error(f"Failed to add tag: {put_resp.text}")
                return False
    except Exception as e:
        logger.error(f"Error updating Shopify tags: {e}")
        return False
