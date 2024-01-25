
from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource, abort
from flask_cors import CORS
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from models import  User, Event, Organizer, Category, BookedEvent, db
 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = 'mysecretkey'

CORS(app)

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

jwt = JWTManager(app)


class Index(Resource):
        def get(self):
         
         response_dict={
             "Message":"Welcome to Event domain API"
         }
        
         return make_response(
             jsonify(response_dict),
             200
         )
    
api.add_resource(Index, '/')

class UserRegistration(Resource):
      #parser = reqparse.RequestParser()
    #parser.add_argument("first_name", required=True, help="First name is required", type=str)
    #parser.add_argument("last_name", required=True, help="Last name is required", type=str)
    #parser.add_argument("username", required=True, help="Username is required", type=str)
    #parser.add_argument("email", required=True, help="Email is required", type=str)
    #parser.add_argument("password", required=True, help="Password is required", tyoe=str)
    
    #@jwt_reuired
    def post(self):
        data = request.get_json()
        
        user = User(
            

            username = data['username'],
            email = data['email'],
            phone_number = data['phone_number'],
            password = data['password'],
                 
        )
        
        access_token = create_access_token(identity= user.username)
        #refresh_token = create_refresh_token(identity= data['username'])
        
        try:
            db.session.add(user)
            db.session.commit()
            
            return {
                'message': f"User '{user.username}' successfully created",
                'access_token': access_token,
                # 'refresh_token': refresh_token
            }, 201
            
        
        except Exception as e:
            db.session.rollback()
            abort(500, error=f"Error creating user: {str(e)}") 
        
        finally:
            db.session.close()
    
    
    def get(self):
        users = User.query.all()
        
        if not users:
            abort(404, message="No user records found")
        
        response = [{
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "password": user.password,
              } for user in users] 
        
        
        return make_response(
            jsonify(response),
            200
        )
    
    
api.add_resource(UserRegistration, '/users/register')


class UserByID(Resource):
     
    @jwt_required()
    def get(self, id):
        with app.app_context():
            current_user = get_jwt_identity()
        
        user = User.query.filter_by(id=id).first()
        
        if not user:
            return make_response(
                jsonify({"Message":"User not found"}),
                404
            )
        
        event_dict =[{
            "id":event.id,
            "title": event.title,
            "description": event.description,
            "image_url":event.image_url,
            "start_time": event.start_time,
            "end_time": event.end_time
            
        } for event in user.events]
        
        response = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "password": user.password,
            "events": event_dict
            
        }
        
        return make_response (
            jsonify(response),
            200
        )
        
        
    
    def patch(self, id):
       
        
        user = User.query.filter_by(id=id).first()
        
        data = request.get_json()
        for attr, value in data.items():
            setattr(user, attr, value)
            
        db.session.add(user)
        db.session.commit()
        

    def delete(self, id):
        user = User.query.filter_by(id=id).first()
        
        if user:
            Event.query.filter_by(user_id=id).delete()
            
            try:
                db.session.delete(user)
                db.session.commit()
                
            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 500
            
            response = make_response(jsonify({'message': 'User record successfully deleted'}), 204)
            return response


api.add_resource(UserByID, '/users/<int:id>')
        
    
class OrganizerRegistration(Resource):
    def post(self):
        data = request.get_json()
        
        organizer = Organizer(
            
            username=data['username'],
            email=data['email'],
            phone_number=data['phone_number'],
            password=data['password'],
                 
        )
        
        try:
            db.session.add(organizer)
            db.session.commit()
            
        
        except Exception as e:
            db.session.rollback()
            abort(500, error=f"Error creating organizer: {str(e)}") 
        
        finally:
            db.session.close()
        
        pass
    
    def get(self):
        organizers = Organizer.query.all()
        
        if not organizers:
            abort(404, message="No organizer records found")
        
        response = [{
            "id": organizer.id,
            "username": organizer.username,
            "email": organizer.email,
            "password": organizer.password,
              } for organizer in organizers] 
        
        
        return make_response(
            jsonify(response),
            200
        )

api.add_resource(OrganizerRegistration, '/organizers')
        
    
class OrganizerByID(Resource):
    
    def get(self, id):
        organizer = Organizer.query.filter_by(id=id).first()
        
        if not organizer:
            return make_response(
                jsonify({"Message":"Organizer not found"}),
                404
            )
        
        event_dict =[{
            "id":event.id,
            "title": event.title,
            "description": event.description,
            "image_url":event.image_url,
            "start_time": event.start_time,
            "end_time": event.end_time
            
        } for event in organizer.events]
        
        response = {
            "id": organizer.id,
            "username": organizer.username,
            "email": organizer.email,
            "password": organizer.password,
            "events": event_dict
            
        }
        
        return make_response (
            jsonify(response),
            200
        )
    
    def patch(self, id):
         
        organizer = Organizer.query.filter_by(id=id).first()
        
        data = request.get_json()
        for attr, value in data.items():
            setattr(organizer, attr, value)
            
        db.session.add(organizer)
        db.session.commit()
        
        
    
    def delete(self, id):
        
        organizer = Organizer.query.filter_by(id=id).first()
        
        if organizer:
            Event.query.filter_by(organizer_id=id).delete()
            
            try:
                db.session.delete(organizer)
                db.session.commit()
                
            except Exception as e:
                db.session.rollback()
                return {'error': str(e)}, 500
            
            response = make_response(jsonify({'Message': 'Organizer record successfully deleted'}), 200)
            return response
            
        
        db.session.delete(organizer)
        db.session.commit()
        
        return make_response({'Message': 'User record successfully deleted'}, 200 )

api.add_resource(OrganizerByID, '/organizers/<int:id>')
        
    
class Events(Resource):
    def get(self): 
        events = Event.query.all()
    
        response= [{
                "id":event.id,
                "title": event.title,
                "description": event.description,
                "image_url":event.image_url,
                "start_time": event.start_time,
                "end_time": event.end_time
            } for event in events ]
            
        if not response:
            jsonify({"error":"Events not found"}, 404) 
        
        return make_response(
            jsonify(response),
            200
        )
            
 
    def post(self):
        
        data = request.get_json()
        
        event = Event (
            title = data['title'],
            description = data['description '],
            image_url = data['image_url'],
            start_time = data['start_time'],
            end_time = data['end_time'],
            organizer_id = data['organizer_id'],
            category_id = data['category_id'],
                       
        )
        
        try: 
            db.session.add(event)
            db.session.commit()
        
        except Exception as e:
            db.session.rollback()
            abort(500, error=f"Error creating an event: {str(e)}")
        
        finally:
             db.session.close()
             
api.add_resource(Events, '/events')
            
            

class EventByID(Resource):
    def get(self, id):
        event = Event.query.filter_by(id=id).first()
        
        if not event:
            return make_response(
                jsonify({'message':'event record not found'}),
                404
            )
        
        response = {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "image_url": event.image_url,
            "start_time": event.start_time,
            "end_time": event.end_time,
            "organizer": event.organizer.username,
            "category": event.category.name
        }

        return make_response(
            jsonify(response),
            200
        )
            
    
    def patch(self, id):
        event = Event.query.filter_by(id=id).first()
        
        data = request.get_json()
        for attr, value in data.items():
            setattr(event , attr, value)
            
        db.session.add(event)
        db.session.commit()
        

    def delete(self, id):
        event = Event.query.filter_by(id=id).first()
        
        db.session.delete(event)
        db.session.commit()
        
        return make_response({'message': 'User record successfully deleted'}, 200 )

api.add_resource(EventByID, '/events/<int:id>')
 
class Categories(Resource):
    def get(self):
        
        categories = Category.query.all()
        
        response = [{
            'id': category.id,
            'name': category.name
        } for category in categories]
        
        return make_response(
            jsonify(response),
            200
        )

api.add_resource(Categories, '/categories')
        
        
class CategoryByID(Resource):
    def get(self, id):
        
        category = Category.query.filter_by(id=id).first()
        
        if not category:
            return make_response(
                jsonify({"error":"Category not Found"}),
                404
                )
        
        else:
            
            event_dict = [{
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "image_url":event.image_url,
                "start_time": event.start_time,
                "end_time": event.end_time
                
            } for event in category.events        
            ]
            
            response_data = {
                "id": category.id,
                "name": category.name,
                "events": event_dict
            }
            
            return make_response(
                jsonify(response_data),
                200
            )
            
api.add_resource(CategoryByID, '/categories/<int:id>')

class BookedEvents(Resource):
    def post(self, id):
        data = request.get_json()
        
        booked_event = BookedEvent (
            
            event_id = data['event_id'],
            user_id = data['user_id'],
            
        )
        
        try: 
            db.session.add(booked_event)
            db.session.commit()
        
        except Exception as e:
            db.session.rollback()
            abort(500, error=f"Error booking an event: {str(e)}")
        
        finally:
             db.session.close()
        
    pass

if __name__ == '__main__':
    app.run(port=5555, debug=True)
    
    
   
    
    
    
    
    




    

