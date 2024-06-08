import os
from dotenv import load_dotenv
from app import create_app, db
from app.models import User, Book

load_dotenv()

app = create_app()

def check_database():
    with app.app_context():
        users = User.query.all()
        if users:
            print("Users:")
            for user in users:
                print(f"ID: {user.id}, Username: {user.username}, Password:{user.password},Role: {user.role}, Reset Token: {user.reset_token}")
        else:
            print("No users found in the database.")
        
        books = Book.query.all()
        if books:
            print("\nBooks:")
            for book in books:
                print(f"ID: {book.id}, Title: {book.title}, Author: {book.author}, File Path: {book.file_path}")
        else:
            print("No books found in the database.")

if __name__ == "__main__":
    check_database()
