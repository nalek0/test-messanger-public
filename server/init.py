import os

from app import app, db

if __name__ == "__main__":
    os.remove("database.db")
    db.create_all(app=app)
