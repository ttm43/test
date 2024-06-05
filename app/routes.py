from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.hazmat.primitives.asymmetric import dh, rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from .models import User, Book
from . import db
from .decorators import login_required
import os
import re

main = Blueprint('main', __name__)


def validate_password(password):
    if len(password) < 15:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    if ' ' in password:
        return False
    return True

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if User.query.filter_by(username=username).first():
            flash('Email is already registered.')
            return redirect(url_for('main.register'))
        
        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('main.register'))
        
        if not validate_password(password):
            flash('Password must be at least 15 characters long, contain both uppercase and lowercase letters, numbers, and special symbols, and cannot contain spaces.')
            return redirect(url_for('main.register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')

@main.route('/check_email', methods=['POST'])
def check_email():
    email = request.form.get('email')
    user = User.query.filter_by(username=email).first()
    if user:
        return jsonify({'exists': True})
    return jsonify({'exists': False})

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if not user:
            flash('Invalid email!')
            return redirect(url_for('main.login'))
        
        if not check_password_hash(user.password, password):
            flash('Invalid username or password!')
            return redirect(url_for('main.login'))
        
        session['user_id'] = user.id
        flash('Login successful!')
        return redirect(url_for('main.index'))
    
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@main.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        
        flash('Password reset link has been sent to your email!')
        return redirect(url_for('main.login'))
    
    return render_template('reset_password.html')

@main.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query')
    results = []
    
    if query:
        results = Book.query.filter((Book.title.contains(query)) | (Book.author.contains(query))).all()
    
    return render_template('search.html', results=results)

@main.route('/books')
@login_required
def books():
    books = Book.query.all()
    return render_template('books.html', books=books)

@main.route('/download/<path:filename>')
@login_required
def download(filename):
    directory = os.path.join(main.root_path, 'static/book')
    return send_from_directory(directory, filename, as_attachment=True)


@main.route('/dh_key_exchange')
def dh_key_exchange():

    parameters = dh.generate_parameters(generator=2, key_size=2048, backend=default_backend())
    server_private_key = parameters.generate_private_key()
    server_public_key = server_private_key.public_key()
    
   
    server_public_key_pem = server_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return server_public_key_pem


@main.route('/sign_data', methods=['POST'])
def sign_data():
    data = request.form.get('data').encode('utf-8')
    
    
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    public_key = private_key.public_key()
    
   
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return jsonify({'signature': signature.hex(), 'public_key': public_key_pem.decode('utf-8')})
