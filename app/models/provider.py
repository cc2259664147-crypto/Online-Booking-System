"""ProviderProfile entity → SQLAlchemy model."""
from app.extensions import db


class ProviderProfile(db.Model):
    __tablename__ = 'provider_profile'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    organization_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)
    approved = db.Column(db.Boolean, default=True)

    user = db.relationship('AppUser', backref='provider_profile', uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "organizationName": self.organization_name,
            "address": self.address,
            "description": self.description,
            "approved": self.approved,
        }
