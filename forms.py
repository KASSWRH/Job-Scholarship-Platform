from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField, 
    TextAreaField, SelectField, FileField, SearchField,
    DateField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, 
    ValidationError, Optional
)
from flask_wtf.file import FileRequired, FileAllowed
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        'Confirm Password', 
        validators=[DataRequired(), EqualTo('password')]
    )
    language_preference = SelectField(
        'Preferred Language', 
        choices=[('en', 'English'), ('ar', 'Arabic')],
        default='en'
    )
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one or login.')

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    language_preference = SelectField(
        'Preferred Language', 
        choices=[('en', 'English'), ('ar', 'Arabic')]
    )
    current_password = PasswordField('Current Password', validators=[Optional()])
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=8)])
    confirm_new_password = PasswordField(
        'Confirm New Password', 
        validators=[Optional(), EqualTo('new_password')]
    )
    submit = SubmitField('Update Profile')
    
    def validate_current_password(self, field):
        if self.new_password.data and not field.data:
            raise ValidationError('Current password is required to set a new password')

class DocumentUploadForm(FlaskForm):
    title = StringField('Document Title', validators=[DataRequired(), Length(max=128)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    document_type = SelectField(
        'Document Type', 
        choices=[
            ('cv', 'Curriculum Vitae (CV)'), 
            ('cover_letter', 'Cover Letter'), 
            ('other', 'Other Document')
        ]
    )
    file = FileField(
        'Document File', 
        validators=[
            FileRequired(), 
            FileAllowed(['pdf', 'doc', 'docx'], 'Only PDF and Word documents are allowed!')
        ]
    )
    submit = SubmitField('Upload Document')

class JobSearchForm(FlaskForm):
    search = SearchField('Search Jobs')
    job_type = SelectField(
        'Job Type', 
        choices=[
            ('', 'All Types'), 
            ('full-time', 'Full Time'), 
            ('part-time', 'Part Time'),
            ('contract', 'Contract'),
            ('internship', 'Internship'),
            ('remote', 'Remote'),
            ('freelance', 'Freelance'),
            ('temporary', 'Temporary'),
            ('volunteer', 'Volunteer')
        ],
        default=''
    )
    location = SelectField(
        'Location',
        choices=[
            ('', 'All Locations'),
            ('remote', 'Remote Only'),
            ('US', 'United States'),
            ('UK', 'United Kingdom'),
            ('CA', 'Canada'),
            ('AU', 'Australia'),
            ('SA', 'Saudi Arabia'),
            ('AE', 'United Arab Emirates'),
            ('EG', 'Egypt'),
            ('JO', 'Jordan'),
            ('KW', 'Kuwait'),
            ('QA', 'Qatar'),
            ('BH', 'Bahrain'),
            ('OM', 'Oman'),
            ('Other', 'Other')
        ],
        default=''
    )
    experience_level = SelectField(
        'Experience Level',
        choices=[
            ('', 'All Levels'),
            ('entry', 'Entry Level'),
            ('mid', 'Mid Level'),
            ('senior', 'Senior Level'),
            ('executive', 'Executive')
        ],
        default=''
    )
    salary_range = SelectField(
        'Salary Range',
        choices=[
            ('', 'Any Salary'),
            ('0-30000', 'Under $30,000'),
            ('30000-60000', '$30,000 - $60,000'),
            ('60000-100000', '$60,000 - $100,000'),
            ('100000-150000', '$100,000 - $150,000'),
            ('150000+', 'Over $150,000')
        ],
        default=''
    )
    industry = SelectField(
        'Industry',
        choices=[
            ('', 'All Industries'),
            ('technology', 'Technology'),
            ('healthcare', 'Healthcare'),
            ('finance', 'Finance & Banking'),
            ('education', 'Education'),
            ('engineering', 'Engineering'),
            ('retail', 'Retail'),
            ('hospitality', 'Hospitality'),
            ('media', 'Media & Communication'),
            ('manufacturing', 'Manufacturing'),
            ('government', 'Government'),
            ('nonprofit', 'Non-Profit'),
            ('other', 'Other')
        ],
        default=''
    )
    date_posted = SelectField(
        'Date Posted',
        choices=[
            ('', 'Any Time'),
            ('1', 'Last 24 Hours'),
            ('7', 'Last 7 Days'),
            ('30', 'Last 30 Days'),
            ('90', 'Last 90 Days')
        ],
        default=''
    )
    sort_by = SelectField(
        'Sort By', 
        choices=[
            ('date', 'Date Posted'),
            ('title', 'Job Title'),
            ('company', 'Company Name'),
            ('relevance', 'Relevance')
        ],
        default='date'
    )
    external_search = BooleanField('Include external sources (Google, LinkedIn)')
    submit = SubmitField('Search')

class ScholarshipSearchForm(FlaskForm):
    search = SearchField('Search Scholarships')
    country = SelectField(
        'Country', 
        choices=[
            ('', 'All Countries'),
            ('US', 'United States'),
            ('UK', 'United Kingdom'),
            ('CA', 'Canada'),
            ('AU', 'Australia'),
            ('SA', 'Saudi Arabia'),
            ('AE', 'United Arab Emirates'),
            ('EG', 'Egypt'),
            ('JO', 'Jordan'),
            ('KW', 'Kuwait'),
            ('QA', 'Qatar'),
            ('BH', 'Bahrain'),
            ('OM', 'Oman'),
            ('Other', 'Other')
        ],
        default=''
    )
    field_of_study = SelectField(
        'Field of Study',
        choices=[
            ('', 'All Fields'),
            ('computer_science', 'Computer Science & IT'),
            ('engineering', 'Engineering'),
            ('medicine', 'Medicine & Health Sciences'),
            ('business', 'Business & Management'),
            ('arts', 'Arts & Humanities'),
            ('science', 'Science'),
            ('education', 'Education'),
            ('law', 'Law'),
            ('social_sciences', 'Social Sciences'),
            ('agriculture', 'Agriculture & Environmental Science'),
            ('mathematics', 'Mathematics & Statistics'),
            ('languages', 'Languages & Linguistics'),
            ('media', 'Media & Communications'),
            ('other', 'Other')
        ],
        default=''
    )
    degree_level = SelectField(
        'Degree Level',
        choices=[
            ('', 'All Degrees'),
            ('bachelor', 'Bachelor\'s'),
            ('master', 'Master\'s'),
            ('phd', 'PhD'),
            ('postdoc', 'Postdoctoral'),
            ('diploma', 'Diploma'),
            ('certificate', 'Certificate'),
            ('other', 'Other')
        ],
        default=''
    )
    funding_type = SelectField(
        'Funding Type',
        choices=[
            ('', 'All Types'),
            ('full', 'Full Funding'),
            ('partial', 'Partial Funding'),
            ('tuition', 'Tuition Only'),
            ('monthly', 'Monthly Stipend'),
            ('research', 'Research Grant'),
            ('travel', 'Travel Grant'),
            ('other', 'Other')
        ],
        default=''
    )
    deadline_period = SelectField(
        'Deadline Period',
        choices=[
            ('', 'Any Time'),
            ('7', 'Within 7 Days'),
            ('30', 'Within 30 Days'),
            ('90', 'Within 90 Days'),
            ('180', 'Within 6 Months'),
            ('365', 'Within 1 Year')
        ],
        default=''
    )
    eligibility = SelectField(
        'Eligibility',
        choices=[
            ('', 'All'),
            ('international', 'International Students'),
            ('local', 'Local Students Only'),
            ('women', 'Women Only'),
            ('minority', 'Minority Groups'),
            ('need_based', 'Need-Based'),
            ('merit_based', 'Merit-Based'),
            ('other', 'Other')
        ],
        default=''
    )
    sort_by = SelectField(
        'Sort By', 
        choices=[
            ('deadline', 'Application Deadline'),
            ('date', 'Date Posted'),
            ('title', 'Scholarship Title'),
            ('amount', 'Funding Amount'),
            ('relevance', 'Relevance')
        ],
        default='deadline'
    )
    external_search = BooleanField('Include external sources (Google Scholar, Academic Portals)')
    submit = SubmitField('Search')
