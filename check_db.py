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
                print(f"Username: {user.username}")
        else:
            print("No users found in the database.")

        
        books = Book.query.all()
        if books:
            print("Books:")
            for book in books:
                print(f"Title: {book.title}, Author: {book.author}, File Path: {book.file_path}")
        else:
            print("No books found in the database.")

if __name__ == '__main__':
    check_database()