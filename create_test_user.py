from app import app, db
from models import User

# Create a test user
with app.app_context():
    # Check if user already exists
    existing_user = User.query.filter_by(email='test@example.com').first()
    
    if existing_user:
        print('Test user already exists!')
    else:
        user = User()
        user.username = 'testuser'
        user.email = 'test@example.com'
        user.first_name = 'Test'
        user.last_name = 'User'
        user.set_password('testpassword')
        
        db.session.add(user)
        db.session.commit()
        
        print('Test user created successfully!')