import os
from dotenv import load_dotenv
from app import create_app, db
from app.models import Book


load_dotenv()


app = create_app()

def add_books():
    with app.app_context():
        
        if not Book.query.first():
            books = [
                Book(title="The Great Gatsby", author="F. Scott Fitzgerald", file_path="static/book/great_gatsby.pdf"),
                Book(title="1984", author="George Orwell", file_path="static/book/1984.pdf"),
                Book(title="To Kill a Mockingbird", author="Harper Lee", file_path="static/book/to_kill_a_mockingbird.pdf"),
                Book(title="Pride and Prejudice", author="Jane Austen", file_path="static/book/pride_and_prejudice.pdf"),
                Book(title="The Catcher in the Rye", author="J.D. Salinger", file_path="static/book/the_catcher_in_the_rye.pdf"),
            ]
            db.session.bulk_save_objects(books)
            db.session.commit()
            print("Books added successfully.")
        else:
            print("Books already exist in the database.")

if __name__ == '__main__':
    add_books()
