from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from .models import User, Book
from . import db, mail
from .decorators import login_required, admin_required
import os
import re
import secrets
from flask_mail import Message

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
        new_user = User(username=username, password=hashed_password, role='user')  
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
        session['role'] = user.role
        flash('Login successful!')
        return redirect(url_for('main.index'))
    
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@main.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(username=email).first() 
        if user:
            token = secrets.token_hex(16)
            user.reset_token = token
            db.session.commit()
            reset_url = url_for('main.reset_token', token=token, _external=True)
            msg = Message('Password Reset Request',
                          recipients=[user.username],  
                          body=f'To reset your password, visit the following link: {reset_url}')
            try:
                mail.send(msg)
                flash('An email has been sent with instructions to reset your password.', 'info')
            except Exception as e:
                flash(f'Failed to send email: {str(e)}', 'danger')
                print(f"Failed to send email: {str(e)}")
            return redirect(url_for('main.login'))
        else:
            flash('No account found with that email.', 'danger')
            return redirect(url_for('main.reset_password'))
    return render_template('reset_password.html')

@main.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = User.query.filter_by(reset_token=token).first_or_404()
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('main.reset_token', token=token))
        user.password = generate_password_hash(password)
        user.reset_token = None
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('main.login'))
    return render_template('reset_token.html', token=token)

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

@main.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    books = Book.query.all()
    return render_template('admin/admin_dashboard.html', users=users, books=books)

@main.route('/make_admin/<int:user_id>')
@login_required
@admin_required
def make_admin(user_id):
    user = User.query.get(user_id)
    if user:
        user.role = 'admin'
        db.session.commit()
        flash(f'User {user.username} is now an admin.')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/upload_book', methods=['POST'])
@login_required
@admin_required
def upload_book():
    title = request.form.get('title')
    author = request.form.get('author')
    file = request.files['file']
    
    if not title or not author or 'file' not in request.files:
        flash('All fields are required.')
        return redirect(url_for('main.admin_dashboard'))
    
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('main.admin_dashboard'))
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(main.root_path, 'static/book', filename)
        file.save(file_path)
        
        new_book = Book(title=title, author=author, file_path='static/book/' + filename)
        db.session.add(new_book)
        db.session.commit()
        
        flash('Book uploaded and added successfully!')
        return redirect(url_for('main.admin_dashboard'))

@main.route('/delete_book/<int:book_id>')
@login_required
@admin_required
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
        flash(f'Book {book.title} has been deleted.')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/delete_user/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Cannot delete admin user!')
        return redirect(url_for('main.admin_dashboard'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!')
    return redirect(url_for('main.admin_dashboard'))
