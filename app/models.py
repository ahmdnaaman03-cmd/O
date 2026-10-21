import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from cryptography.fernet import Fernet

db = SQLAlchemy()

# إعداد التشفير
def get_cipher():
    key = os.environ.get('ENCRYPTION_KEY')
    if not key:
        raise ValueError("ENCRYPTION_KEY is missing in environment variables")
    return Fernet(key.encode())

def encrypt_data(data: str) -> str:
    if not data: return data
    return get_cipher().encrypt(data.encode()).decode()

def decrypt_data(token: str) -> str:
    if not token: return token
    try:
        return get_cipher().decrypt(token.encode()).decode()
    except Exception:
        return token # Fallback if already decrypted or invalid

class Merchant(db.Model):
    __tablename__ = 'merchants'
    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(100), nullable=False)
    store_url = db.Column(db.String(255), unique=True, nullable=False)
    webhook_secret = db.Column(db.String(100)) # Shopify HMAC Secret
    whatsapp_app_secret = db.Column(db.String(255)) # WhatsApp HMAC Secret
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    orders = db.relationship('Order', backref='merchant', lazy=True)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    shopify_order_id = db.Column(db.String(100), nullable=False)
    _customer_phone = db.Column('customer_phone', db.String(255), nullable=False) # Encrypted
    status = db.Column(db.String(50), default='pending_whatsapp_sent') # State Machine
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Property to handle automatic encryption/decryption
    @property
    def customer_phone(self):
        return decrypt_data(self._customer_phone)

    @customer_phone.setter
    def customer_phone(self, value):
        self._customer_phone = encrypt_data(value)

    # Mandatory Merchant Isolation Query Helper
    @classmethod
    def get_by_merchant(cls, merchant_id):
        return cls.query.filter_by(merchant_id=merchant_id)
