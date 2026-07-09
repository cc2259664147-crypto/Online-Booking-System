from flask import Flask, render_template
from models import db
from appointment_routes import appointment_bp

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///appointments.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.register_blueprint(appointment_bp)

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/booking-page")
def booking_page():
    return render_template("booking.html")

@app.route("/my-booking")
def my_booking():
    return render_template("my_booking.html")

@app.route("/login")
def login():
    return render_template("log_in.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/more")
def more():
    return render_template("more.html")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5000)