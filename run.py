"""Entry point — mirrors BookingApplication.java main method."""
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Java version ran on port 9090 (application.yml)
    app.run(debug=True, port=9090)
