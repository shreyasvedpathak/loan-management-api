# Internal imports
from app import db, bcrypt
from app.constants import *

# External imports
import uuid
import datetime

class Users(db.Model):
    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key=True)
    pub_id = db.Column(db.String, unique=True)
    username = db.Column(db.String, index=True,
                         nullable=False, unique=True)
    role = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String, index=True, nullable=False)
    contact = db.Column(db.String, nullable=False)
    password = db.Column(db.String)
    timestamp = db.Column(db.DateTime, nullable=False)
    approved = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self, username, email, contact, password, role=ROLE['CUSTOMER'], approved=True):
        self.pub_id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.contact = contact
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.role = role
        self.timestamp = datetime.datetime.now(datetime.timezone.utc)
        self.approved = approved

