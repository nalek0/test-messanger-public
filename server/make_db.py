import os

from app import create_app
from database import db

try:
    os.remove("database.db")
except FileNotFoundError:
    pass
db.create_all(app=create_app())
