import os
from flask import Flask
from routes import routes_bp 
from flask_socketio import SocketIO, emit

# Create Flask application
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Ensure CORS is handled
app.debug = True 
app.register_blueprint(routes_bp)

from extensions import db, login_manager
from models import *
# Configuration
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or 'sqlite:///app.db'
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import routes after app initialization
with app.app_context():
    import routes
    import auth
    db.create_all()


@socketio.on("connect")
def handle_connect():
    print("Receiver connected!")


@socketio.on("food_request")
def handle_food_request(data):
    print("Handling food request")
    """
    Handles a new food donation request from an NGO and notifies all receivers.
    """
    donation_id = data.get("donation_id")
    ngo_name = data.get("ngo_name")
    food_type = data.get("food_type")
    quantity = data.get("quantity")

    if not all([donation_id, ngo_name, food_type, quantity]):
        return emit("error", {"message": "Invalid request data"})

    emit("new_food_request", {
        "donation_id": donation_id,
        "ngo_name": ngo_name,
        "food_type": food_type,
        "quantity": quantity
    }, broadcast=True)
    print("Emitted the food request")


@socketio.on("receiver_response")
def handle_receiver_response(data):
    """
    Handles the response from a receiver (accept or decline) and updates the donation status.
    """
    donation_id = data.get("donation_id")
    accepted = data.get("accepted")
    print(data.get("accepted"))

    donation = FoodDonation.query.get(donation_id)
    if not donation:
        return emit("error", {"message": "Donation not found"})

    if accepted:
        donation.status = "assigned"
        db.session.commit()
        print("Accepted Notification sent to dashboard")
        emit("accept_notify", broadcast=True)
    else:
        emit("decline_notify", broadcast=True)  # Added status

if __name__ == '__main__':
    socketio.run(app, debug=True)