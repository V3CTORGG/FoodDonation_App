🍽️ Food Donation App






A web and mobile platform that helps NGOs, donors, and food receivers connect efficiently for surplus food redistribution. The system ensures real-time tracking, request handling, and seamless food redirection to orphanages and needy communities.

✨ Features

🔑 User Authentication for NGOs, Donors, and Receivers

📍 Live Tracking using Leaflet.js

📦 Order Management System

📸 Food Image Upload

📊 Dashboard with Order History

🚀 Real-time Notifications using Socket.io

🗺 Route Optimization & Tracking

📸 Screenshots

🎯 NGO Dashboard



📍 Live Tracking with Route Optimization



🏗 Tech Stack

Frontend: HTML, CSS, JavaScript, Bootstrap, Leaflet.js

Backend: Flask (Python), Socket.io

Database: PostgreSQL / MySQL

Mobile App: React Native (Coming soon)

APIs: Google Maps API for routing & location tracking

🚀 Installation & Setup

🔧 Prerequisites

Python 3.8+

Flask & Dependencies (pip install -r requirements.txt)

PostgreSQL/MySQL Database

🔹 Clone the Repository

 git clone https://github.com/yourusername/surplus-food-redistribution.git
 cd surplus-food-redistribution

🔹 Install Dependencies

pip install -r requirements.txt

🔹 Set Up Database

flask db init
flask db migrate -m "Initial Migration"
flask db upgrade

🔹 Run the Server

flask run

The app will be available at http://127.0.0.1:5000

⚡ API Endpoints

Method

Endpoint

Description

POST

/register

Register NGO/Receiver

POST

/login

User login

POST

/donate

Add a new donation

GET

/donations

Get active donations

POST

/accept_donation

NGO accepts a donation

POST

/find_receivers

Find nearby receivers

📜 License

This project is licensed under the MIT License. See the LICENSE file for more details.

🤝 Contributing

Fork the repository 🍴

Create a new branch (git checkout -b feature-branch)

Commit your changes (git commit -m 'Added a cool feature')

Push to your branch (git push origin feature-branch)

Create a Pull Request 🔥

📬 Contact

For any queries or collaborations, reach out to:
📧 your.email@example.com📌 LinkedIn🌍 GitHub

🚀 Let's reduce food waste and help those in need!

