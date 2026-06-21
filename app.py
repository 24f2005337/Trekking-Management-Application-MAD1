from flask import Flask, render_template
from applications.models import db, User
import os

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret-trekking-key'

db.init_app(app)

# Database Setup & Default Admin
with app.app_context():
    db.create_all()
    
    admin_user = User.query.filter_by(role='admin').first()
    if not admin_user:
        default_admin = User(
            username='admin',
            email='admin@trekking.com',
            password='admin123',
            role='admin'
        )
        db.session.add(default_admin)
        db.session.commit()
        print("Admin created programmatically!")

with app.app_context():
    import applications.controllers



if __name__ == '__main__':
    app.run(debug=True, port=5000)