from models import db
from models import FoodDonation

def delete_all_orders():
    try:
        db.session.query(FoodDonation).delete()
        db.session.commit()
        print("✅ All orders deleted successfully!")
    except Exception as e:
        db.session.rollback()
        print("❌ Error:", e)
