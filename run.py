from dotenv import load_dotenv
import os
from app import create_app, db

load_dotenv()  

app = create_app()

with app.app_context():
    db.create_all()  

if __name__ == '__main__':
    app.run(debug=True)
