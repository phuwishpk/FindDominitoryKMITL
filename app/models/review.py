from datetime import datetime
from app.extensions import db

class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    
    # หมายเหตุ: ในระบบนี้ user อาจเป็น Owner หรือ Admin
    # เราจะใช้ user_id จาก Principal object (current_user.ref_id)
    user_id = db.Column(db.Integer, nullable=False)
    
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False) # คะแนน 1-5
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Review id={self.id} prop_id={self.property_id} rating={self.rating}>"