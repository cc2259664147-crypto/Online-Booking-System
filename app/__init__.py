from flask import Flask
from app.config import Config
from app.extensions import db, bcrypt


def create_app():
    """Flask application factory."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.services import service_bp
    from app.routes.appointments import appointment_bp
    from app.routes.reviews import review_bp
    from app.routes.complaints import complaint_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(service_bp, url_prefix='/api/services')
    app.register_blueprint(appointment_bp, url_prefix='/api/appointments')
    app.register_blueprint(review_bp, url_prefix='/api/reviews')
    app.register_blueprint(complaint_bp, url_prefix='/api/complaints')

    # Global error handler (like GlobalExceptionHandler.java)
    @app.errorhandler(RuntimeError)
    def handle_runtime_error(e):
        return {"error": str(e)}, 400

    @app.errorhandler(Exception)
    def handle_generic_error(e):
        return {"error": str(e)}, 500

    # Create tables
    with app.app_context():
        db.create_all()

    return app
