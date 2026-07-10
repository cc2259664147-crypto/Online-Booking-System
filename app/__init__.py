from flask import Flask, render_template, request
from app.config import Config
from app.extensions import db, bcrypt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.services import service_bp
    from app.routes.appointments import appointment_bp
    from app.routes.reviews import review_bp
    from app.routes.complaints import complaint_bp
    from app.models.feedback import Feedback  # ensure table is created

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(service_bp, url_prefix="/api/services")
    app.register_blueprint(appointment_bp, url_prefix="/api/appointments")
    app.register_blueprint(review_bp, url_prefix="/api/reviews")
    app.register_blueprint(complaint_bp, url_prefix="/api/complaints")

    @app.route("/")
    @app.route("/home")
    def home():
        return render_template("home.html")

    @app.route("/login")
    def login_page():
        return render_template("log_in.html")

    @app.route("/register")
    def register_page():
        return render_template("register.html")

    @app.route("/booking-page")
    def booking_page():
        return render_template("booking.html")

    @app.route("/my-booking")
    def my_booking():
        return render_template("my_booking.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/contact")
    def contact():
        return render_template("contact.html")

    @app.route("/more")
    def more():
        return render_template("more.html")

    @app.route("/feedback", methods=["POST"])
    def feedback():
        from app.models.feedback import Feedback
        message = (request.form.get("message") or "").strip()
        if message:
            fb = Feedback(content=message)
            db.session.add(fb)
            db.session.commit()
        return render_template("contact.html", submitted=True)

    @app.errorhandler(RuntimeError)
    def handle_runtime_error(e):
        return {"error": str(e)}, 400

    @app.errorhandler(Exception)
    def handle_generic_error(e):
        return {"error": str(e)}, 500

    with app.app_context():
        db.create_all()
        _seed_services()

    return app


def _seed_services():
    """Seed medical_service table so frontend booking options match the DB."""
    from app.models.medical_service import MedicalService

    existing_names = {s.name for s in MedicalService.query.all()}

    services = [
        # 综合（首页评价用）
        ("综合评价", "综合", "平台总体评价", 0),
        # 内科
        ("感冒", "内科", "常见上呼吸道感染", 50),
        ("发烧", "内科", "体温升高相关诊疗", 50),
        ("咳嗽", "内科", "呼吸道刺激反应诊疗", 50),
        ("高血压", "内科", "慢性高血压诊疗", 80),
        ("糖尿病", "内科", "血糖代谢疾病诊疗", 80),
        # 外科
        ("外伤处理", "外科", "外部伤口清理与包扎", 60),
        ("伤口换药", "外科", "术后或外伤换药", 40),
        ("术后复查", "外科", "手术后复查", 70),
        ("手术咨询", "外科", "手术方案咨询", 30),
        # 儿科
        ("儿童发烧", "儿科", "儿童发烧诊疗", 50),
        ("儿童咳嗽", "儿科", "儿童咳嗽诊疗", 50),
        ("疫苗接种", "儿科", "儿童疫苗接种", 100),
        ("儿童体检", "儿科", "儿童常规体检", 80),
        # 口腔科
        ("洗牙", "口腔科", "超声波洗牙", 120),
        ("补牙", "口腔科", "龋齿补牙修复", 200),
        ("拔牙", "口腔科", "牙齿拔除", 150),
        ("牙齿矫正", "口腔科", "牙齿矫正咨询与方案", 300),
        # 眼科
        ("视力检查", "眼科", "常规视力检查", 40),
        ("近视检查", "眼科", "近视度数测量", 50),
        ("眼干眼涩", "眼科", "干眼症诊疗", 60),
        ("结膜炎", "眼科", "结膜炎诊疗", 55),
        # 皮肤科
        ("过敏", "皮肤科", "皮肤过敏诊疗", 55),
        ("湿疹", "皮肤科", "湿疹诊疗", 60),
        ("痤疮", "皮肤科", "痤疮（青春痘）诊疗", 65),
        ("皮肤瘙痒", "皮肤科", "皮肤瘙痒症状诊疗", 50),
    ]

    added = 0
    for name, category, desc, price in services:
        if name not in existing_names:
            db.session.add(MedicalService(
                name=name, category=category,
                description=desc, price=price, active=True,
            ))
            added += 1
    if added:
        db.session.commit()