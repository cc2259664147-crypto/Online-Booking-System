"""Java enums → Python enums."""
import enum


class UserRole(enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class AppointmentStatus(enum.Enum):
    BOOKED = "BOOKED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
