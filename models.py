from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    language_preference = db.Column(db.String(10), default='en')  # 'en' for English, 'ar' for Arabic
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    documents = db.relationship('Document', backref='owner', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    saved_jobs = db.relationship('SavedJob', backref='user', lazy='dynamic')
    saved_scholarships = db.relationship('SavedScholarship', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(256), nullable=False)
    file_type = db.Column(db.String(32), nullable=False)  # 'cv', 'cover_letter', 'other'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DocumentTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    template_type = db.Column(db.String(32), nullable=False)  # 'cv', 'cover_letter'
    template_content = db.Column(db.Text, nullable=False)
    is_arabic = db.Column(db.Boolean, default=False)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    company = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(128))
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    salary_range = db.Column(db.String(64))
    job_type = db.Column(db.String(32))  # full-time, part-time, contract, etc.
    url = db.Column(db.String(256))  # original job posting URL
    is_arabic = db.Column(db.Boolean, default=False)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    saved_by = db.relationship('SavedJob', backref='job', lazy='dynamic')

class Scholarship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    organization = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    eligibility = db.Column(db.Text)
    amount = db.Column(db.String(64))
    deadline = db.Column(db.DateTime)
    country = db.Column(db.String(64))
    field_of_study = db.Column(db.String(128))
    url = db.Column(db.String(256))  # original scholarship posting URL
    is_arabic = db.Column(db.Boolean, default=False)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    saved_by = db.relationship('SavedScholarship', backref='scholarship', lazy='dynamic')

class SavedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

class SavedScholarship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scholarship_id = db.Column(db.Integer, db.ForeignKey('scholarship.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(32))  # 'job', 'scholarship', 'system'
    is_read = db.Column(db.Boolean, default=False)
    related_id = db.Column(db.Integer)  # ID of related job or scholarship
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
