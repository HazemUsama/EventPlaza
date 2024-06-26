#!/usr/bin/env python3
"""This module defines the User model for EventPlaza"""
import secrets
from .base_model import BaseModel
from itsdangerous import URLSafeTimedSerializer as Serializer
from .event_tables import event_organizers, event_attendens
from event_plaza import login_manager, db, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(user_id)

class User(BaseModel, db.Model, UserMixin):
    """This class defines the User model for EventPlaza"""
    __tablename__ = 'users'

    first_name = db.Column(db.String(128), nullable=True)
    last_name = db.Column(db.String(128), nullable=True)
    email = db.Column(db.String(128), nullable=False, unique=True)
    image_file = db.Column(db.String(32), nullable=False, default='default.jpg')
    password = db.Column(db.String(128), nullable=False)
    email_token = db.Column(db.String(128), nullable=False, default='NOT INIT')
    is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    managed_events = db.relationship('Event', secondary='event_managers',
                                     back_populates='managers', lazy=True)
    organized_events = db.relationship('Event', secondary='event_organizers',
                                    back_populates='organizer', lazy=True)
    attended_events = db.relationship('Event', secondary='event_attendens',
                                   back_populates='attendees', lazy=True)
    assigned_tasks = db.relationship('Task', secondary='assigns',
                                    back_populates='assignees', lazy=True)
    member_committees = db.relationship('Committee', secondary='committee_member',
                                     back_populates='members', lazy=True)
    vice_committees = db.relationship('Committee', secondary='committee_vice',
                                   back_populates='vices', lazy=True)
    head_committees = db.relationship('Committee', secondary='committee_head',
                                   back_populates='heads', lazy=True)

    def get_reset_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})
    
    def verify_email_token(self, token):
        return self.email_token == token

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, 300)['user_id']
        except:
            return None
        return User.query.get(user_id)