from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask import Blueprint
from extensions import db
from models import User, FoodDonation
from geopy.geocoders import Nominatim
from datetime import datetime
from simple_websocket import Server
from functools import wraps
import json

# Rest of your routes code stays the same
routes_bp = Blueprint('routes', __name__)
# WebSocket connections store
ws_connections = {
    'ngo': {},  # ngo_id: websocket
    'receiver': {}  # receiver_id: websocket
}

def ws_route(f):
    @wraps(f)
    def wrapped(ws, *args, **kwargs):
        try:
            return f(ws, *args, **kwargs)
        except Exception as e:
            print(f"WebSocket error: {e}")
            return None
    return wrapped

@routes_bp.route('/ws')
@ws_route
def websocket(ws):
    if not current_user.is_authenticated:
        return

    # Store the WebSocket connection based on user type
    if current_user.user_type == 'ngo':
        ws_connections['ngo'][current_user.id] = ws
    else:
        ws_connections['receiver'][current_user.id] = ws

    while True:
        try:
            # Keep the connection alive and handle incoming messages
            message = ws.receive()
            if message is None:
                break

            # Handle incoming messages if needed
            data = json.loads(message)
            # Add message handling logic here

        except Exception as e:
            print(f"WebSocket error: {e}")
            break

    # Clean up connection when done
    if current_user.user_type == 'ngo':
        ws_connections['ngo'].pop(current_user.id, None)
    else:
        ws_connections['receiver'].pop(current_user.id, None)

@routes_bp.route('/send_receiver_request/<int:donation_id>/<int:receiver_id>', methods=['POST'])
@login_required
def send_receiver_request(donation_id, receiver_id):
    if current_user.user_type != 'ngo':
        return jsonify({'success': False})

    donation = FoodDonation.query.get_or_404(donation_id)
    receiver = User.query.get_or_404(receiver_id)

    if donation.assigned_ngo_id != current_user.id or receiver.user_type != 'receiver':
        return jsonify({'success': False})

    # Send notification to receiver through WebSocket if connected
    receiver_ws = ws_connections['receiver'].get(receiver_id)
    if receiver_ws:
        receiver_ws.send(json.dumps({
            'type': 'food_request',
            'donation_id': donation_id,
            'ngo_id': current_user.id,
            'ngo_name': current_user.name,
            'food_type': donation.food_type,
            'quantity': donation.quantity
        }))
        return jsonify({'success': True})

    return jsonify({'success': False, 'message': 'Receiver is not online'})

@routes_bp.route('/receiver_response/<int:donation_id>', methods=['POST'])
@login_required
def receiver_response(donation_id):
    if current_user.user_type != 'receiver':
        return jsonify({'success': False})

    data = request.get_json()
    accepted = data.get('accepted', False)

    donation = FoodDonation.query.get_or_404(donation_id)
    ngo_ws = ws_connections['ngo'].get(donation.assigned_ngo_id)

    if ngo_ws:
        ngo_ws.send(json.dumps({
            'type': 'receiver_response',
            'donation_id': donation_id,
            'receiver_id': current_user.id,
            'receiver_name': current_user.name,
            'accepted': accepted
        }))
        return jsonify({'success': True})

    return jsonify({'success': False, 'message': 'NGO is not online'})

@routes_bp.route('/')
def index():
    return redirect(url_for('routes.login'))

@routes_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            if user.user_type == 'ngo':
                return redirect(url_for('routes.ngo_dashboard'))
            else:
                return redirect(url_for('routes.receiver_dashboard'))
        flash('Invalid email or password')
    return render_template('login.html')

@routes_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        name = request.form.get('name')
        address = request.form.get('address')
        phone = request.form.get('phone')

        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('routes.register'))

        # Geocode address
        geolocator = Nominatim(user_agent="food_waste_app")
        location = geolocator.geocode(address)

        if not location:
            flash('Invalid address')
            return redirect(url_for('routes.register'))

        user = User(
            email=email,
            user_type=user_type,
            name=name,
            address=address,
            latitude=location.latitude,
            longitude=location.longitude,
            phone=phone
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Registration successful')
        return redirect(url_for('routes.login'))

    return render_template('register.html')

@routes_bp.route('/donor_form', methods=['GET', 'POST'])
def donor_form():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        food_type = request.form.get('food_type')
        quantity = request.form.get('quantity')

        # Geocode address
        geolocator = Nominatim(user_agent="food_waste_app")
        location = geolocator.geocode(address)

        if not location:
            flash('Invalid address')
            return redirect(url_for('routes.donor_form'))

        donation = FoodDonation(
            donor_name=name,
            donor_phone=phone,
            donor_address=address,
            latitude=location.latitude,
            longitude=location.longitude,
            food_type=food_type,
            quantity=quantity
        )

        db.session.add(donation)
        db.session.commit()

        flash('Donation submitted successfully')
        return redirect(url_for('routes.donor_form'))

    return render_template('donor_form.html')

@routes_bp.route('/ngo_dashboard')
@login_required
def ngo_dashboard():
    if current_user.user_type != 'ngo':
        return redirect(url_for('routes.login'))

    # Get donations assigned to this NGO or available ones
    donations = FoodDonation.query.filter(
        (FoodDonation.assigned_ngo_id == current_user.id) |
        (FoodDonation.status == 'available')
    ).all()

    return render_template('ngo_dashboard.html', donations=donations)

@routes_bp.route('/accept_donation/<int:donation_id>', methods=['POST'])
@login_required
def accept_donation(donation_id):
    if current_user.user_type != 'ngo':
        return jsonify({'success': False})

    donation = FoodDonation.query.get_or_404(donation_id)
    if donation.status == 'available':
        donation.status = 'accepted'
        donation.assigned_ngo_id = current_user.id
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@routes_bp.route('/mark_picked_up/<int:donation_id>', methods=['POST'])
@login_required
def mark_picked_up(donation_id):
    if current_user.user_type != 'ngo':
        return jsonify({'success': False})

    donation = FoodDonation.query.get_or_404(donation_id)
    if donation.status == 'accepted' and donation.assigned_ngo_id == current_user.id:
        donation.status = 'picked_up'
        donation.pickup_time = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@routes_bp.route('/find_receivers/<int:donation_id>')
@login_required
def find_receivers(donation_id):
    if current_user.user_type != 'ngo':
        return jsonify({'success': False})

    donation = FoodDonation.query.get_or_404(donation_id)
    if donation.assigned_ngo_id != current_user.id:
        return jsonify({'success': False})

    # Find receivers within 10km radius
    receivers = User.query.filter_by(user_type='receiver').all()
    nearby_receivers = []

    for receiver in receivers:
        distance = donation.distance_to(receiver.latitude, receiver.longitude)
        if distance <= 10:  # 10 km radius
            nearby_receivers.append({
                'id': receiver.id,
                'name': receiver.name,
                'distance': distance,
                'address': receiver.address
            })

    return jsonify({
        'success': True,
        'receivers': sorted(nearby_receivers, key=lambda x: x['distance'])
    })

@routes_bp.route('/assign_receiver/<int:donation_id>/<int:receiver_id>', methods=['POST'])
@login_required
def assign_receiver(donation_id, receiver_id):
    if current_user.user_type != 'ngo':
        return jsonify({'success': False})

    donation = FoodDonation.query.get_or_404(donation_id)
    receiver = User.query.get_or_404(receiver_id)

    if donation.assigned_ngo_id == current_user.id and receiver.user_type == 'receiver':
        donation.assigned_receiver_id = receiver_id
        donation.status = 'assigned'
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@routes_bp.route('/receiver_dashboard')
@login_required
def receiver_dashboard():
    if current_user.user_type != 'receiver':
        return redirect(url_for('routes.login'))

    assigned_donations = FoodDonation.query.filter_by(
        assigned_receiver_id=current_user.id
    ).all()
    return render_template('receiver_dashboard.html', donations=assigned_donations)

@routes_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.login'))