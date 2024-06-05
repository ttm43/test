import os
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User

app = create_app()
app.app_context().push()

def add_admin(username, password):
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    admin_user = User(username=username, password=hashed_password, role='admin')
    db.session.add(admin_user)
    db.session.commit()
    print(f'Admin user {username} added successfully.')

if __name__ == '__main__':
    username = input('Enter admin username (email): ')
    password = input('Enter admin password: ')
    add_admin(username, password)
