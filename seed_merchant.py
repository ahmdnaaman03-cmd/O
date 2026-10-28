from app import create_app
from app.models import db, Merchant

app = create_app()
with app.app_context():
    # إنشاء الجداول لو مش موجودة
    db.create_all()

    store_url = "aman-test-store-c9korns0.myshopify.com"
    store_name = "aman-test-store"
    webhook_secret = "3ccb3e98377b6a70988a10ee0f7526c58101e1c2e128a8da4e0e9577d78eec3b"

    # التأكد لو المتجر موجود نحدث بياناته، لو مش موجود نضيفه
    merchant = Merchant.query.filter_by(store_url=store_url).first()
    if not merchant:
        merchant = Merchant(
            store_name=store_name,
            store_url=store_url,
            webhook_secret=webhook_secret
        )
        db.session.add(merchant)
        print("✅ Test Merchant created successfully!")
    else:
        merchant.store_name = store_name
        merchant.webhook_secret = webhook_secret
        print("✅ Test Merchant updated successfully!")

    db.session.commit()
