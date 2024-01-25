from app import app, db
from models import Event, Organizer, User, Category
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

with app.app_context():
     Event.query.delete()
     Organizer.query.delete()
     User.query.delete()
     Category.query.delete()
     
     print ("Seeding Users...")
     
     users = []
     for _ in range(5):
        user = User(username=fake.unique.user_name(), email=fake.unique.email(), phone_number=fake.unique.phone_number(), password=fake.password())
        users.append(user)
     db.session.add_all(users)
     db.session.commit()
     
     print("Seeding Organizers...")
     
     organizers = []
     
     for _ in range(5):
        organizer = Organizer(username=fake.unique.user_name(), email=fake.unique.email(), phone_number=fake.unique.phone_number(), password=fake.password())
        organizers.append(organizer)
     db.session.add_all(organizers)
     db.session.commit()
     
     print('Seeding  Categories...')
     categories = []
     for _ in range(6):
        category = Category(name=fake.word())
        categories.append(category)
     db.session.add_all(categories)
     db.session.commit()
     
     print("Seeding Events...")
     
     events = []
     for _ in range(10):
        title = fake.sentence()
        description = fake.paragraph()
        image_url = fake.image_url()
        start_time = fake.date_time_between(start_date='now', end_date='+30d')
        end_time = start_time + timedelta(hours=random.randint(1, 6))

        organizer = random.choice(organizers)
        category = random.choice(categories)
        user = random.choice(users)

        event = Event(
            title=title,
            description=description,
            image_url=image_url,
            start_time=start_time,
            end_time=end_time,
            organizer_id=organizer.id,
            category_id=category.id,
            user_id=user.id
        )

        events.append(event)

     db.session.add_all(events)
     db.session.commit()
     
     print('Done seeding!')
     

