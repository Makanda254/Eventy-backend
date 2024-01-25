#import jwt
#from flask import current_app

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from flask_restful import abort

from datetime import datetime, timedelta



db = SQLAlchemy()

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    serialize_rules = ('-events.user',)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(450), nullable=False)
    
    events = db.relationship('Event', secondary='booked_events', back_populates='users')
    #def generate_token(self, username, id):
        
        #try:
            #object_data = {
               #"initial_time": datetime.utcnow ,
               #"end_time"   : datetime.utcnow + timedelta(minutes=60),
               #"username" : username,
               # "user_id": id
               # #}
            #token = jwt.encode(object_data, str(current)
                #object_data, 
                #str(current_app.os.getenv('SECRET_KEY')), 
                #algorithm='HS256'
            #)
            
            #return token
            
        #except Exception as e:
            #return str(e)
            
    #def decode_token(self, token)
        #token_data = jwt.decode(token,
                                #str(current_app.os.getenv('SECRET_KEY')),
                                #algorithms='HS256')
        
        #return token_data
        
    
    @validates('username')
    def checks_uniqueness(self, key, username):
        if User.query.filter_by(username=username).first():
            abort(400, 
                message=f"A user with the name '{username}' already exists. Please choose a different name."
            )
        else:
            return username

class Organizer(db.Model, SerializerMixin):
    __tablename__ = 'organizers'
    serialize_rules = ('-events.organizer',)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(450), nullable=False)
   
    
    events = db.relationship('Event', backref='organizer', lazy=True)
    
    @validates('username')
    def checks_uniqueness(self, key, username):
        if Organizer.query.filter_by(username=username).first():
            abort(400, 
                message=f"A user with the name '{username}' already exists. Please choose a different name."
            )
        else:
            return username

class Event(db.Model, SerializerMixin):
    __tablename__ = 'events'
    serialize_rules = ('-users.events', '-organizer.events', '-category.events',)
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    organizer_id = db.Column(db.Integer, db.ForeignKey('organizers.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    users = db.relationship('User', secondary='booked_events', back_populates='events')

class Category(db.Model, SerializerMixin):
    __tablename__ = 'categories'
    serialize_rules = ('-events.category',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    events = db.relationship('Event', backref='category', lazy=True)
    
class BookedEvent(db.Model, SerializerMixin):
    __tablename__ = 'booked_events'
    
    serialize_rules = ('-user.booked_events', '-event.booked_events',)
    
    id = db.Column(db.Integer, primary_key= True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
