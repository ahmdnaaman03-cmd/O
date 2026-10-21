from app import create_app
from app.models import db, Merchant

app = create_app()
with app.app_context():
    # إنشاء الجداول لو مش موجودة
    db.create_all()
    
    # التأكد إن التاجر مش موجود قبل إضافته
    merchant = Merchant.query.filter_by(store_url="test-store.myshopify.com").first()
    if not merchant:
        merchant = Merchant(
            store_name="Test Store",
            store_url="test-store.myshopify.com",
            webhook_secret="my_super_secret_hmac_key"
        )
        db.session.add(merchant)
        db.session.commit()
        print("✅ Test Merchant created successfully!")
    else:
        print("✅ Test Merchant already exists.")
