import os
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import func, case
import logging
from web_scraper import get_website_text_content, get_job_listings, get_scholarship_listings, is_valid_url

logger = logging.getLogger(__name__)

from models import (
    User, Document, DocumentTemplate, Job, Scholarship, 
    SavedJob, SavedScholarship, Notification
)
from forms import (
    LoginForm, RegistrationForm, DocumentUploadForm, 
    JobSearchForm, ScholarshipSearchForm, ProfileForm
)
from app import db
from utilities import allowed_file, extract_keywords
from document_generator import generate_cv, generate_cover_letter

def register_routes(app):
    # Make models available to templates
    from models import Notification
    app.jinja_env.globals.update(Notification=Notification)
    
    # Home page
    @app.route('/')
    def index():
        recent_jobs = Job.query.order_by(Job.posted_at.desc()).limit(4).all()
        recent_scholarships = Scholarship.query.order_by(Scholarship.posted_at.desc()).limit(4).all()
        
        return render_template(
            'index.html', 
            recent_jobs=recent_jobs, 
            recent_scholarships=recent_scholarships
        )

    # Authentication routes
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            flash('Invalid email or password', 'danger')
        
        return render_template('login.html', form=form)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User()
            user.username = form.username.data
            user.email = form.email.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.language_preference = form.language_preference.data
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))

    # Dashboard and profile routes
    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Count user's documents
        doc_count = Document.query.filter_by(user_id=current_user.id).count()
        
        # Get saved jobs and scholarships
        saved_jobs = SavedJob.query.filter_by(user_id=current_user.id).count()
        saved_scholarships = SavedScholarship.query.filter_by(user_id=current_user.id).count()
        
        # Get unread notifications
        notifications = Notification.query.filter_by(
            user_id=current_user.id, 
            is_read=False
        ).order_by(Notification.created_at.desc()).limit(5).all()
        
        # Get recent jobs and scholarships
        recent_jobs = Job.query.order_by(Job.posted_at.desc()).limit(3).all()
        recent_scholarships = Scholarship.query.order_by(
            Scholarship.posted_at.desc()
        ).limit(3).all()
        
        return render_template(
            'dashboard.html',
            doc_count=doc_count,
            saved_jobs=saved_jobs,
            saved_scholarships=saved_scholarships,
            notifications=notifications,
            recent_jobs=recent_jobs,
            recent_scholarships=recent_scholarships
        )

    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        form = ProfileForm(obj=current_user)
        
        if form.validate_on_submit():
            current_user.username = form.username.data
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.language_preference = form.language_preference.data
            
            if form.new_password.data:
                current_user.set_password(form.new_password.data)
                
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
            
        return render_template('profile.html', form=form)

    # Job routes
    @app.route('/jobs', methods=['GET'])
    def jobs():
        form = JobSearchForm(request.args)
        page = request.args.get('page', 1, type=int)
        
        # Retrieve form data
        search = request.args.get('search', '')
        job_type = request.args.get('job_type', '')
        location = request.args.get('location', '')
        experience_level = request.args.get('experience_level', '')
        salary_range = request.args.get('salary_range', '')
        industry = request.args.get('industry', '')
        date_posted = request.args.get('date_posted', '')
        sort_by = request.args.get('sort_by', 'date')
        external_search = request.args.get('external_search', 'False') == 'True'
        
        # Set the form values
        form.search.data = search
        form.job_type.data = job_type
        form.location.data = location
        form.experience_level.data = experience_level
        form.salary_range.data = salary_range
        form.industry.data = industry
        form.date_posted.data = date_posted
        form.sort_by.data = sort_by
        form.external_search.data = external_search
        
        # Base query
        query = Job.query
        
        # Apply filters
        if search:
            search_terms = search.split()
            for term in search_terms:
                search_term = f"%{term}%"
                query = query.filter(
                    (Job.title.ilike(search_term)) | 
                    (Job.description.ilike(search_term)) |
                    (Job.company.ilike(search_term)) |
                    (Job.requirements.ilike(search_term))
                )
                
        # Handle external search if selected
        external_jobs = []
        if external_search and search:
            try:
                # Define sources for job listings
                job_sources = [
                    f"https://www.google.com/search?q={'+'.join(search.split())}+jobs",
                    f"https://www.indeed.com/jobs?q={'+'.join(search.split())}",
                    f"https://www.linkedin.com/jobs/search/?keywords={'+'.join(search.split())}"
                ]
                
                # Add location to search if specified
                if location:
                    job_sources = [f"{source}+in+{location}" for source in job_sources]
                    
                # Get results from multiple sources
                for source_url in job_sources[:2]:  # Try first 2 sources
                    if is_valid_url(source_url):
                        external_results = get_job_listings(source_url)
                        if external_results:
                            # Add each job result as a temporary job object
                            for job_info in external_results:
                                temp_job = Job()
                                temp_job.id = -1 - len(external_jobs)  # Use a negative ID to indicate it's not in the DB
                                temp_job.title = job_info.get("title", "Job Title Not Available")
                                temp_job.company = job_info.get("company", "Company Not Available")
                                temp_job.location = job_info.get("location", "Location Not Available")
                                temp_job.description = job_info.get("description_snippet", "No description available. Click to view on source website.")
                                temp_job.requirements = "See full job descriptions on the source website."
                                temp_job.job_type = job_info.get("job_type", "Not Specified")
                                temp_job.url = job_info.get("source_url", source_url)
                                temp_job.is_arabic = False
                                temp_job.posted_at = datetime.utcnow()
                                external_jobs.append(temp_job)
            except Exception as e:
                logger.error(f"Error fetching external jobs: {str(e)}")
            
        if job_type:
            query = query.filter(Job.job_type == job_type)
            
        if location:
            if location == 'remote':
                # For remote jobs, look for remote type or location containing remote keywords
                query = query.filter(
                    (Job.job_type == 'remote') | 
                    (Job.location.ilike('%remote%')) | 
                    (Job.location.ilike('%work from home%')) |
                    (Job.location.ilike('%wfh%'))
                )
            else:
                query = query.filter(Job.location.ilike(f"%{location}%"))
        
        # Filter by experience level
        if experience_level:
            if experience_level == 'entry':
                query = query.filter(
                    Job.requirements.ilike('%entry%') | 
                    Job.requirements.ilike('%junior%') | 
                    Job.requirements.ilike('%0-2 years%') | 
                    Job.requirements.ilike('%0-1 year%') |
                    Job.requirements.ilike('%fresh graduate%')
                )
            elif experience_level == 'mid':
                query = query.filter(
                    Job.requirements.ilike('%mid%') | 
                    Job.requirements.ilike('%intermediate%') | 
                    Job.requirements.ilike('%2-5 years%') | 
                    Job.requirements.ilike('%3-5 years%')
                )
            elif experience_level == 'senior':
                query = query.filter(
                    Job.requirements.ilike('%senior%') | 
                    Job.requirements.ilike('%5-8 years%') | 
                    Job.requirements.ilike('%5+ years%') | 
                    Job.requirements.ilike('%7+ years%')
                )
            elif experience_level == 'executive':
                query = query.filter(
                    Job.requirements.ilike('%executive%') | 
                    Job.requirements.ilike('%director%') | 
                    Job.requirements.ilike('%chief%') | 
                    Job.requirements.ilike('%10+ years%') |
                    Job.requirements.ilike('%15+ years%')
                )
                
        # Filter by salary range
        if salary_range:
            if salary_range == '0-30000':
                query = query.filter(
                    Job.salary_range.ilike('%$0%') | 
                    Job.salary_range.ilike('%$1%') | 
                    Job.salary_range.ilike('%$2%') | 
                    Job.salary_range.ilike('%under $30%')
                )
            elif salary_range == '30000-60000':
                query = query.filter(
                    Job.salary_range.ilike('%$3%') | 
                    Job.salary_range.ilike('%$4%') | 
                    Job.salary_range.ilike('%$5%')
                )
            elif salary_range == '60000-100000':
                query = query.filter(
                    Job.salary_range.ilike('%$6%') | 
                    Job.salary_range.ilike('%$7%') | 
                    Job.salary_range.ilike('%$8%') | 
                    Job.salary_range.ilike('%$9%')
                )
            elif salary_range == '100000-150000':
                query = query.filter(
                    Job.salary_range.ilike('%$10%') | 
                    Job.salary_range.ilike('%$11%') | 
                    Job.salary_range.ilike('%$12%') | 
                    Job.salary_range.ilike('%$13%') | 
                    Job.salary_range.ilike('%$14%')
                )
            elif salary_range == '150000+':
                query = query.filter(
                    Job.salary_range.ilike('%$15%') | 
                    Job.salary_range.ilike('%$16%') | 
                    Job.salary_range.ilike('%$17%') | 
                    Job.salary_range.ilike('%$18%') | 
                    Job.salary_range.ilike('%$19%') | 
                    Job.salary_range.ilike('%$20%') | 
                    Job.salary_range.ilike('%$25%') | 
                    Job.salary_range.ilike('%$30%')
                )
        
        # Filter by industry
        if industry:
            query = query.filter(
                Job.description.ilike(f"%{industry}%") | 
                Job.company.ilike(f"%{industry}%") |
                Job.title.ilike(f"%{industry}%")
            )
            
        # Filter by date posted
        if date_posted:
            days_ago = datetime.utcnow() - timedelta(days=int(date_posted))
            query = query.filter(Job.posted_at >= days_ago)
            
        # Sort results
        if sort_by == 'date':
            query = query.order_by(Job.posted_at.desc())
        elif sort_by == 'title':
            query = query.order_by(Job.title)
        elif sort_by == 'company':
            query = query.order_by(Job.company)
        elif sort_by == 'relevance' and search:
            # Sort by relevance when search term provided
            query = query.order_by(
                case(
                    # Title exact match gets highest priority
                    (func.lower(Job.title) == search.lower(), 1),
                    # Title starts with search term
                    (func.lower(Job.title).ilike(f"{search.lower()}%"), 2),
                    # Title contains search term
                    (func.lower(Job.title).ilike(f"%{search.lower()}%"), 3),
                    # Company name matches
                    (func.lower(Job.company).ilike(f"%{search.lower()}%"), 4),
                    # Everything else
                    else_=5
                ),
                Job.posted_at.desc()
            )
        
        # Execute query with pagination
        jobs = query.paginate(page=page, per_page=10)
        
        # Get user's saved jobs if logged in
        saved_job_ids = []
        if current_user.is_authenticated:
            saved_job_ids = [sj.job_id for sj in SavedJob.query.filter_by(user_id=current_user.id).all()]
            
        # Handle external search if enabled
        external_results = []
        if external_search and search:
            # For now, we'll use a predefined set of job board URLs to scrape
            # In a full implementation, this would be more dynamic and configurable
            job_boards = [
                f"https://www.indeed.com/jobs?q={search.replace(' ', '+')}&l={location if location else ''}",
                f"https://www.linkedin.com/jobs/search/?keywords={search.replace(' ', '+')}&location={location if location else ''}",
                f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={search.replace(' ', '+')}&locT=N&locId=0"
            ]
            
            try:
                # Let the user know we're processing
                flash('جارِ البحث في مواقع الوظائف الخارجية...', 'info' if current_user.language_preference == 'ar' else 'info')
                
                # Search multiple sites to get real data
                for url in job_boards[:2]:
                    if is_valid_url(url):
                        job_data = get_job_listings(url)
                        if job_data:
                            # Process and add all real job listings
                            logger.info(f"Found {len(job_data)} jobs from {url}")
                            if len(job_data) > 0:
                                external_results.append({
                                    "title": f"وظائف من {url.split('/')[2]}" if current_user.language_preference == 'ar' else f"Jobs from {url.split('/')[2]}",
                                    "source": url,
                                    "count": f"{len(job_data)} نتيجة" if current_user.language_preference == 'ar' else f"{len(job_data)} results"
                                })
                            
                if not external_results:
                    flash(
                        'لم يتم العثور على نتائج خارجية. حاول تحسين معايير البحث الخاصة بك.' if current_user.language_preference == 'ar' else 'No external results found. Try refining your search.', 
                        'warning'
                    )
            except Exception as e:
                logger.error(f"Error in external job search: {str(e)}")
                flash(
                    f'خطأ في البحث في المواقع الخارجية: {str(e)}' if current_user.language_preference == 'ar' else f'Error searching external sites: {str(e)}', 
                    'danger'
                )
            
        return render_template(
            'jobs.html', 
            jobs=jobs, 
            form=form, 
            saved_job_ids=saved_job_ids,
            external_results=external_results
        )

    @app.route('/jobs/<int:job_id>')
    def job_detail(job_id):
        job = Job.query.get_or_404(job_id)
        is_saved = False
        
        if current_user.is_authenticated:
            is_saved = SavedJob.query.filter_by(
                user_id=current_user.id, 
                job_id=job.id
            ).first() is not None
            
        # Get related jobs based on title or company
        related_jobs = Job.query.filter(
            ((Job.title.ilike(f"%{job.title.split()[0]}%")) | 
             (Job.company == job.company)) & 
            (Job.id != job.id)
        ).limit(3).all()
        
        # Get CV templates for this job
        cv_templates = DocumentTemplate.query.filter_by(
            template_type='cv',
            is_arabic=(job.is_arabic == True)
        ).all()
        
        # Get cover letter templates for this job
        cover_letter_templates = DocumentTemplate.query.filter_by(
            template_type='cover_letter',
            is_arabic=(job.is_arabic == True)
        ).all()
        
        return render_template(
            'job_detail.html', 
            job=job, 
            is_saved=is_saved,
            related_jobs=related_jobs,
            cv_templates=cv_templates,
            cover_letter_templates=cover_letter_templates
        )

    @app.route('/save_job/<int:job_id>', methods=['POST'])
    @login_required
    def save_job(job_id):
        job = Job.query.get_or_404(job_id)
        
        # Check if already saved
        existing = SavedJob.query.filter_by(
            user_id=current_user.id, 
            job_id=job.id
        ).first()
        
        if existing:
            flash('This job is already saved', 'info')
        else:
            saved_job = SavedJob()
            saved_job.user_id = current_user.id
            saved_job.job_id = job.id
            db.session.add(saved_job)
            db.session.commit()
            flash('Job saved successfully!', 'success')
            
        return redirect(url_for('job_detail', job_id=job.id))
    
    @app.route('/unsave_job/<int:job_id>', methods=['POST'])
    @login_required
    def unsave_job(job_id):
        saved_job = SavedJob.query.filter_by(
            user_id=current_user.id, 
            job_id=job_id
        ).first_or_404()
        
        db.session.delete(saved_job)
        db.session.commit()
        flash('Job removed from saved items', 'info')
        
        return redirect(url_for('job_detail', job_id=job_id))

    # Scholarship routes
    @app.route('/scholarships', methods=['GET'])
    def scholarships():
        form = ScholarshipSearchForm(request.args)
        page = request.args.get('page', 1, type=int)
        
        # Retrieve form data
        search = request.args.get('search', '')
        country = request.args.get('country', '')
        field_of_study = request.args.get('field_of_study', '')
        degree_level = request.args.get('degree_level', '')
        funding_type = request.args.get('funding_type', '')
        deadline_period = request.args.get('deadline_period', '')
        eligibility = request.args.get('eligibility', '')
        sort_by = request.args.get('sort_by', 'deadline')
        external_search = request.args.get('external_search', 'False') == 'True'
        
        # Set the form values
        form.search.data = search
        form.country.data = country
        form.field_of_study.data = field_of_study
        form.degree_level.data = degree_level
        form.funding_type.data = funding_type
        form.deadline_period.data = deadline_period
        form.eligibility.data = eligibility
        form.sort_by.data = sort_by
        form.external_search.data = external_search
        
        # Base query
        query = Scholarship.query
        
        # Apply filters
        if search:
            search_terms = search.split()
            for term in search_terms:
                search_term = f"%{term}%"
                query = query.filter(
                    (Scholarship.title.ilike(search_term)) | 
                    (Scholarship.description.ilike(search_term)) |
                    (Scholarship.organization.ilike(search_term)) |
                    (Scholarship.eligibility.ilike(search_term))
                )
                
        # Handle external search if selected
        external_scholarships = []
        if external_search and search:
            try:
                # Define sources for scholarship listings
                scholarship_sources = [
                    f"https://www.google.com/search?q={'+'.join(search.split())}+scholarship",
                    f"https://www.scholars4dev.com/search/{'+'.join(search.split())}",
                    f"https://www.scholarships.com/scholarship-search?q={'+'.join(search.split())}"
                ]
                
                # Add field of study to search if specified
                if field_of_study:
                    scholarship_sources = [f"{source}+{field_of_study}" for source in scholarship_sources]
                    
                # Add country to search if specified
                if country:
                    scholarship_sources = [f"{source}+in+{country}" for source in scholarship_sources]
                    
                # Get results from multiple sources
                for source_url in scholarship_sources[:2]:  # Try first 2 sources
                    if is_valid_url(source_url):
                        external_results = get_scholarship_listings(source_url)
                        if external_results:
                            # Add each scholarship result as a temporary object
                            for scholarship_info in external_results:
                                temp_scholarship = Scholarship()
                                temp_scholarship.id = -1 - len(external_scholarships)  # Use a negative ID to indicate it's not in the DB
                                temp_scholarship.title = scholarship_info.get("title", "Scholarship Title Not Available")
                                temp_scholarship.organization = scholarship_info.get("organization", "Organization Not Available")
                                temp_scholarship.country = scholarship_info.get("country", country if country else "Various Countries")
                                temp_scholarship.field_of_study = scholarship_info.get("field_of_study", field_of_study if field_of_study else "Various Fields")
                                temp_scholarship.description = scholarship_info.get("description_snippet", "No description available. Click to view on source website.")
                                temp_scholarship.eligibility = scholarship_info.get("eligibility", "See full details on the source website.")
                                temp_scholarship.amount = scholarship_info.get("amount", "See details")
                                temp_scholarship.url = scholarship_info.get("source_url", source_url)
                                temp_scholarship.is_arabic = False
                                temp_scholarship.posted_at = datetime.utcnow()
                                
                                # Try to parse deadline if available, otherwise use default
                                deadline_str = scholarship_info.get("deadline")
                                if deadline_str and isinstance(deadline_str, str):
                                    try:
                                        # Try different date formats
                                        for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y', '%B %d, %Y'):
                                            try:
                                                temp_scholarship.deadline = datetime.strptime(deadline_str, fmt)
                                                break
                                            except ValueError:
                                                continue
                                        
                                        # If parsing failed, use default
                                        if not temp_scholarship.deadline:
                                            temp_scholarship.deadline = datetime.utcnow() + timedelta(days=90)
                                    except:
                                        temp_scholarship.deadline = datetime.utcnow() + timedelta(days=90)
                                else:
                                    temp_scholarship.deadline = datetime.utcnow() + timedelta(days=90)
                                    
                                external_scholarships.append(temp_scholarship)
            except Exception as e:
                logger.error(f"Error fetching external scholarships: {str(e)}")
            
        if country:
            query = query.filter(Scholarship.country == country)
            
        if field_of_study:
            # Now that field_of_study is a SelectField with predefined options
            if field_of_study == 'computer_science':
                query = query.filter(
                    Scholarship.field_of_study.ilike('%computer%') |
                    Scholarship.field_of_study.ilike('%IT%') |
                    Scholarship.field_of_study.ilike('%information technology%') |
                    Scholarship.field_of_study.ilike('%software%')
                )
            elif field_of_study == 'engineering':
                query = query.filter(
                    Scholarship.field_of_study.ilike('%engineering%') |
                    Scholarship.field_of_study.ilike('%mechanical%') |
                    Scholarship.field_of_study.ilike('%electrical%') |
                    Scholarship.field_of_study.ilike('%civil%')
                )
            elif field_of_study == 'medicine':
                query = query.filter(
                    Scholarship.field_of_study.ilike('%medicine%') |
                    Scholarship.field_of_study.ilike('%medical%') |
                    Scholarship.field_of_study.ilike('%health%') |
                    Scholarship.field_of_study.ilike('%nursing%') |
                    Scholarship.field_of_study.ilike('%pharmacy%')
                )
            elif field_of_study == 'business':
                query = query.filter(
                    Scholarship.field_of_study.ilike('%business%') |
                    Scholarship.field_of_study.ilike('%management%') |
                    Scholarship.field_of_study.ilike('%finance%') |
                    Scholarship.field_of_study.ilike('%accounting%') |
                    Scholarship.field_of_study.ilike('%economics%') |
                    Scholarship.field_of_study.ilike('%MBA%')
                )
            elif field_of_study == 'arts':
                query = query.filter(
                    Scholarship.field_of_study.ilike('%arts%') |
                    Scholarship.field_of_study.ilike('%humanities%') |
                    Scholarship.field_of_study.ilike('%literature%') |
                    Scholarship.field_of_study.ilike('%philosophy%') |
                    Scholarship.field_of_study.ilike('%history%')
                )
            elif field_of_study == 'science':
                query = query.filter(
                    Scholarship.field_of_study.ilike('%science%') |
                    Scholarship.field_of_study.ilike('%biology%') |
                    Scholarship.field_of_study.ilike('%chemistry%') |
                    Scholarship.field_of_study.ilike('%physics%')
                )
            elif field_of_study != 'other':  # Handle all other specific options
                query = query.filter(Scholarship.field_of_study.ilike(f"%{field_of_study}%"))
        
        # Filter by degree level
        if degree_level:
            if degree_level == 'bachelor':
                query = query.filter(
                    Scholarship.description.ilike('%bachelor%') |
                    Scholarship.description.ilike('%undergraduate%') |
                    Scholarship.description.ilike('%B.A.%') |
                    Scholarship.description.ilike('%B.S.%') |
                    Scholarship.description.ilike('%B.Sc%')
                )
            elif degree_level == 'master':
                query = query.filter(
                    Scholarship.description.ilike('%master%') |
                    Scholarship.description.ilike('%graduate%') |
                    Scholarship.description.ilike('%M.A.%') |
                    Scholarship.description.ilike('%M.S.%') |
                    Scholarship.description.ilike('%M.Sc%') |
                    Scholarship.description.ilike('%MBA%')
                )
            elif degree_level == 'phd':
                query = query.filter(
                    Scholarship.description.ilike('%phd%') |
                    Scholarship.description.ilike('%Ph.D.%') |
                    Scholarship.description.ilike('%doctorate%') |
                    Scholarship.description.ilike('%doctoral%')
                )
            elif degree_level == 'postdoc':
                query = query.filter(
                    Scholarship.description.ilike('%postdoc%') |
                    Scholarship.description.ilike('%post-doc%') |
                    Scholarship.description.ilike('%post doctoral%')
                )
            elif degree_level != 'other':
                query = query.filter(Scholarship.description.ilike(f"%{degree_level}%"))
                
        # Filter by funding type
        if funding_type:
            if funding_type == 'full':
                query = query.filter(
                    Scholarship.description.ilike('%full%fund%') |
                    Scholarship.description.ilike('%fully funded%') |
                    Scholarship.description.ilike('%complete scholarship%') |
                    Scholarship.amount.ilike('%full%')
                )
            elif funding_type == 'partial':
                query = query.filter(
                    Scholarship.description.ilike('%partial%') |
                    Scholarship.description.ilike('%part fund%') |
                    Scholarship.amount.ilike('%partial%')
                )
            elif funding_type == 'tuition':
                query = query.filter(
                    Scholarship.description.ilike('%tuition%') |
                    Scholarship.description.ilike('%fee waiver%') |
                    Scholarship.amount.ilike('%tuition%')
                )
            elif funding_type != 'other':
                query = query.filter(
                    Scholarship.description.ilike(f"%{funding_type}%") |
                    Scholarship.amount.ilike(f"%{funding_type}%")
                )
            
        # Filter by deadline period
        if deadline_period:
            days = int(deadline_period)
            future_date = datetime.utcnow() + timedelta(days=days)
            query = query.filter(Scholarship.deadline <= future_date)
            
        # Filter by eligibility
        if eligibility:
            if eligibility == 'international':
                query = query.filter(
                    Scholarship.eligibility.ilike('%international%') |
                    Scholarship.description.ilike('%international student%') |
                    Scholarship.description.ilike('%foreign student%')
                )
            elif eligibility == 'local':
                query = query.filter(
                    Scholarship.eligibility.ilike('%local%') |
                    Scholarship.eligibility.ilike('%domestic%') |
                    Scholarship.eligibility.ilike('%citizens only%') |
                    Scholarship.eligibility.ilike('%residents only%')
                )
            elif eligibility == 'women':
                query = query.filter(
                    Scholarship.eligibility.ilike('%women%') |
                    Scholarship.eligibility.ilike('%female%') |
                    Scholarship.description.ilike('%women only%')
                )
            elif eligibility == 'minority':
                query = query.filter(
                    Scholarship.eligibility.ilike('%minority%') |
                    Scholarship.eligibility.ilike('%underrepresented%') |
                    Scholarship.description.ilike('%minority group%')
                )
            elif eligibility != 'other':
                query = query.filter(
                    Scholarship.eligibility.ilike(f"%{eligibility}%") |
                    Scholarship.description.ilike(f"%{eligibility}%")
                )
            
        # Sort results
        if sort_by == 'deadline':
            # Sort by closest deadline first, nulls last
            query = query.order_by(
                case(
                    (Scholarship.deadline == None, 1),
                    else_=0
                ),
                Scholarship.deadline
            )
        elif sort_by == 'date':
            query = query.order_by(Scholarship.posted_at.desc())
        elif sort_by == 'title':
            query = query.order_by(Scholarship.title)
        elif sort_by == 'amount':
            # This would be complex in reality - here we'll just do a simple approach
            # We'd need to convert amount to a numeric field for proper sorting
            query = query.order_by(Scholarship.amount.desc())
        elif sort_by == 'relevance' and search:
            # Sort by relevance when search term provided
            query = query.order_by(
                case(
                    # Title exact match gets highest priority
                    (func.lower(Scholarship.title) == search.lower(), 1),
                    # Title starts with search term
                    (func.lower(Scholarship.title).ilike(f"{search.lower()}%"), 2),
                    # Title contains search term
                    (func.lower(Scholarship.title).ilike(f"%{search.lower()}%"), 3),
                    # Organization name matches
                    (func.lower(Scholarship.organization).ilike(f"%{search.lower()}%"), 4),
                    # Everything else
                    else_=5
                ),
                Scholarship.deadline,
                Scholarship.posted_at.desc()
            )
            
        # Execute query with pagination
        scholarships = query.paginate(page=page, per_page=10)
        
        # Get user's saved scholarships if logged in
        saved_scholarship_ids = []
        if current_user.is_authenticated:
            saved_scholarship_ids = [ss.scholarship_id for ss in 
                                    SavedScholarship.query.filter_by(user_id=current_user.id).all()]
        
        # Handle external search if enabled
        external_results = []
        if external_search and search:
            # For now, we'll use a predefined set of scholarship sites to scrape
            # In a full implementation, this would be more dynamic and configurable
            scholarship_sites = [
                f"https://www.scholars4dev.com/tag/{search.replace(' ', '-')}/",
                f"https://www.scholarships.com/financial-aid/college-scholarships/scholarship-directory/academic-major/{search.replace(' ', '-')}",
                f"https://www.internationalscholarships.com/search?q={search.replace(' ', '+')}"
            ]
            
            try:
                # Let the user know we're processing
                flash('جارِ البحث في قواعد بيانات المنح الدراسية الخارجية...' if current_user.language_preference == 'ar' else 'Searching external scholarship databases...', 'info')
                
                # Search multiple sites for real scholarship data
                for url in scholarship_sites[:2]:
                    if is_valid_url(url):
                        scholarship_data = get_scholarship_listings(url)
                        if scholarship_data:
                            # Process and add all real scholarship listings
                            logger.info(f"Found {len(scholarship_data)} scholarships from {url}")
                            if len(scholarship_data) > 0:
                                external_results.append({
                                    "title": f"منح دراسية من {url.split('/')[2]}" if current_user.language_preference == 'ar' else f"Scholarships from {url.split('/')[2]}",
                                    "source": url,
                                    "count": f"{len(scholarship_data)} نتيجة" if current_user.language_preference == 'ar' else f"{len(scholarship_data)} results"
                                })
                            
                if not external_results:
                    flash(
                        'لم يتم العثور على نتائج خارجية. حاول تحسين معايير البحث الخاصة بك.' if current_user.language_preference == 'ar' else 'No external results found. Try refining your search.', 
                        'warning'
                    )
            except Exception as e:
                logger.error(f"Error in external scholarship search: {str(e)}")
                flash(
                    f'خطأ في البحث في المواقع الخارجية: {str(e)}' if current_user.language_preference == 'ar' else f'Error searching external sites: {str(e)}', 
                    'danger'
                )
            
        return render_template(
            'scholarships.html', 
            scholarships=scholarships, 
            form=form, 
            saved_scholarship_ids=saved_scholarship_ids,
            external_results=external_results
        )

    @app.route('/scholarships/<int:scholarship_id>')
    def scholarship_detail(scholarship_id):
        scholarship = Scholarship.query.get_or_404(scholarship_id)
        is_saved = False
        
        if current_user.is_authenticated:
            is_saved = SavedScholarship.query.filter_by(
                user_id=current_user.id, 
                scholarship_id=scholarship.id
            ).first() is not None
            
        # Get related scholarships
        related_scholarships = Scholarship.query.filter(
            ((Scholarship.field_of_study == scholarship.field_of_study) | 
            (Scholarship.organization == scholarship.organization)) & 
            (Scholarship.id != scholarship.id)
        ).limit(3).all()
        
        return render_template(
            'scholarship_detail.html', 
            scholarship=scholarship, 
            is_saved=is_saved,
            related_scholarships=related_scholarships
        )

    @app.route('/save_scholarship/<int:scholarship_id>', methods=['POST'])
    @login_required
    def save_scholarship(scholarship_id):
        scholarship = Scholarship.query.get_or_404(scholarship_id)
        
        # Check if already saved
        existing = SavedScholarship.query.filter_by(
            user_id=current_user.id, 
            scholarship_id=scholarship.id
        ).first()
        
        if existing:
            flash('This scholarship is already saved', 'info')
        else:
            saved_scholarship = SavedScholarship()
            saved_scholarship.user_id = current_user.id
            saved_scholarship.scholarship_id = scholarship.id
            db.session.add(saved_scholarship)
            db.session.commit()
            flash('Scholarship saved successfully!', 'success')
            
        return redirect(url_for('scholarship_detail', scholarship_id=scholarship.id))
    
    @app.route('/unsave_scholarship/<int:scholarship_id>', methods=['POST'])
    @login_required
    def unsave_scholarship(scholarship_id):
        saved_scholarship = SavedScholarship.query.filter_by(
            user_id=current_user.id, 
            scholarship_id=scholarship_id
        ).first_or_404()
        
        db.session.delete(saved_scholarship)
        db.session.commit()
        flash('Scholarship removed from saved items', 'info')
        
        return redirect(url_for('scholarship_detail', scholarship_id=scholarship_id))

    # Document management routes
    @app.route('/documents')
    @login_required
    def documents():
        user_documents = Document.query.filter_by(user_id=current_user.id).order_by(
            Document.updated_at.desc()
        ).all()
        
        # Group documents by type
        cv_documents = [doc for doc in user_documents if doc.file_type == 'cv']
        cover_letter_documents = [doc for doc in user_documents if doc.file_type == 'cover_letter']
        other_documents = [doc for doc in user_documents if doc.file_type not in ['cv', 'cover_letter']]
        
        return render_template(
            'documents.html',
            cv_documents=cv_documents,
            cover_letter_documents=cover_letter_documents,
            other_documents=other_documents
        )

    @app.route('/upload_document', methods=['GET', 'POST'])
    @login_required
    def upload_document():
        form = DocumentUploadForm()
        
        if form.validate_on_submit():
            file = form.file.data
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"{current_user.id}_{timestamp}_{filename}"
                
                # Save the file
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Create document record
                document = Document()
                document.title = form.title.data
                document.description = form.description.data
                document.file_path = filename
                document.file_type = form.document_type.data
                document.user_id = current_user.id
                
                db.session.add(document)
                db.session.commit()
                
                flash('Document uploaded successfully!', 'success')
                return redirect(url_for('documents'))
            else:
                flash('Invalid file type', 'danger')
                
        return render_template('upload_document.html', form=form)

    @app.route('/document/<int:document_id>')
    @login_required
    def view_document(document_id):
        document = Document.query.get_or_404(document_id)
        
        # Check if user owns the document
        if document.user_id != current_user.id:
            flash('You do not have permission to view this document', 'danger')
            return redirect(url_for('documents'))
            
        return send_from_directory(
            app.config['UPLOAD_FOLDER'], 
            document.file_path, 
            as_attachment=True
        )

    @app.route('/delete_document/<int:document_id>', methods=['POST'])
    @login_required
    def delete_document(document_id):
        document = Document.query.get_or_404(document_id)
        
        # Check if user owns the document
        if document.user_id != current_user.id:
            flash('You do not have permission to delete this document', 'danger')
            return redirect(url_for('documents'))
            
        # Delete the file
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], document.file_path))
        except Exception as e:
            logging.error(f"Failed to delete file: {e}")
            
        # Delete the database record
        db.session.delete(document)
        db.session.commit()
        
        flash('Document deleted successfully', 'success')
        return redirect(url_for('documents'))

    # Document generation routes
    @app.route('/document_templates')
    @login_required
    def document_templates():
        # Get CV templates
        cv_templates = DocumentTemplate.query.filter_by(
            template_type='cv',
            is_arabic=(current_user.language_preference == 'ar')
        ).all()
        
        # Get cover letter templates
        cover_letter_templates = DocumentTemplate.query.filter_by(
            template_type='cover_letter',
            is_arabic=(current_user.language_preference == 'ar')
        ).all()
        
        return render_template(
            'document_templates.html',
            cv_templates=cv_templates,
            cover_letter_templates=cover_letter_templates
        )

    @app.route('/create_document/<string:template_type>/<int:template_id>', methods=['GET', 'POST'])
    @login_required
    def create_document(template_type, template_id):
        template = DocumentTemplate.query.get_or_404(template_id)
        
        if request.method == 'POST':
            document_data = request.form.to_dict()
            
            # Generate document based on template type
            if template_type == 'cv':
                filename = generate_cv(
                    user=current_user,
                    template=template,
                    data=document_data,
                    upload_folder=app.config['UPLOAD_FOLDER']
                )
            else:  # cover_letter
                filename = generate_cover_letter(
                    user=current_user,
                    template=template,
                    data=document_data,
                    upload_folder=app.config['UPLOAD_FOLDER']
                )
                
            # Create document record
            document = Document()
            document.title = document_data.get('title', f"Generated {template_type.capitalize()}")
            document.description = document_data.get('description', '')
            document.file_path = filename
            document.file_type = template_type
            document.user_id = current_user.id
            
            db.session.add(document)
            db.session.commit()
            
            flash(f'{template_type.capitalize()} generated successfully!', 'success')
            return redirect(url_for('documents'))
            
        return render_template(
            'create_document.html',
            template=template,
            template_type=template_type
        )

    # Notification routes
    @app.route('/notifications')
    @login_required
    def notifications():
        page = request.args.get('page', 1, type=int)
        notifications = Notification.query.filter_by(
            user_id=current_user.id
        ).order_by(Notification.created_at.desc()).paginate(
            page=page, per_page=20
        )
        
        return render_template('notifications.html', notifications=notifications)

    @app.route('/mark_notification_read/<int:notification_id>', methods=['POST'])
    @login_required
    def mark_notification_read(notification_id):
        notification = Notification.query.get_or_404(notification_id)
        
        # Check if notification belongs to user
        if notification.user_id != current_user.id:
            return jsonify({'success': False}), 403
            
        notification.is_read = True
        db.session.commit()
        
        return jsonify({'success': True})

    @app.route('/mark_all_notifications_read', methods=['POST'])
    @login_required
    def mark_all_notifications_read():
        Notification.query.filter_by(
            user_id=current_user.id, 
            is_read=False
        ).update({Notification.is_read: True})
        
        db.session.commit()
        flash('All notifications marked as read', 'success')
        
        return redirect(url_for('notifications'))

    # Language toggle
    @app.route('/set_language/<string:lang>')
    @login_required
    def set_language(lang):
        if lang in ['en', 'ar']:
            current_user.language_preference = lang
            db.session.commit()
            
        return redirect(request.referrer or url_for('index'))
        
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
