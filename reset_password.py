from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    user = User.query.filter_by(username='admin').first()
    if user:
        user.password_hash = generate_password_hash('admin')
        db.session.commit()
        print("Password for 'admin' reset to 'admin'.")
    else:
        print("User 'admin' not found. Creating it.")
        new_user = User(username='admin')
        new_user.set_password('admin')
        db.session.add(new_user)
        db.session.commit()
        print("User 'admin' created with password 'admin'.")
