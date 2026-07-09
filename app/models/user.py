"""AppUser entity → SQLAlchemy model."""
from app.extensions import db, bcrypt
from app.models.enums import UserRole


class AppUser(db.Model):
    __tablename__ = 'app_user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    gender = db.Column(db.String(10), nullable=True, default="")
    age = db.Column(db.Integer, nullable=True)

    def set_password(self, raw_password):
        self.password = bcrypt.generate_password_hash(raw_password).decode('utf-8')

    def check_password(self, raw_password):
        return bcrypt.check_password_hash(self.password, raw_password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role.value if self.role else None,
            "phone": self.phone,
            "gender": self.gender or "",
            "age": self.age,
        }
