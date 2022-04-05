import os

from app import create_app
from database import db

os.remove("database.db")
db.create_all(app=create_app())