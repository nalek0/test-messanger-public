from app import create_app
from database import db
db.create_all(app=create_app())
