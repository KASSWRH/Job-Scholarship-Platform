from app import app, db
from models import User, Job, Scholarship, DocumentTemplate
from datetime import datetime, timedelta
import random

def create_sample_jobs():
    # Clear existing jobs
    Job.query.delete()
    
    # Job types
    job_types = ['full-time', 'part-time', 'contract', 'internship', 'remote', 'freelance']
    
    # Company names
    companies = [
        'Tech Solutions Inc', 'Global Systems', 'Data Innovators', 
        'Smart Solutions', 'Future Technologies', 'Digital Experts',
        'Innovative AI', 'Cloud Computing Co.', 'Mobile App Builders',
        'Web Development Pro', 'IT Security Solutions', 'Software Engineering Ltd'
    ]
    
    # Locations
    locations = [
        'New York, US', 'San Francisco, US', 'London, UK', 'Toronto, CA',
        'Berlin, Germany', 'Dubai, AE', 'Cairo, EG', 'Riyadh, SA',
        'Remote', 'Hybrid - Chicago, US', 'Jeddah, SA', 'Amman, JO'
    ]
    
    # Salary ranges
    salary_ranges = [
        '$25,000 - $35,000', '$40,000 - $55,000', '$60,000 - $80,000',
        '$85,000 - $110,000', '$120,000 - $150,000', '$160,000+',
        'Competitive', 'Based on experience', 'Negotiable'
    ]
    
    job_titles = [
        'Software Engineer', 'Frontend Developer', 'Backend Developer',
        'Full Stack Developer', 'DevOps Engineer', 'Data Scientist',
        'UI/UX Designer', 'Product Manager', 'QA Engineer',
        'System Administrator', 'Machine Learning Engineer', 'Mobile Developer',
        'Database Administrator', 'Technical Support Specialist', 'IT Security Analyst'
    ]
    
    arabic_job_titles = [
        'مهندس برمجيات', 'مطور واجهة أمامية', 'مطور خلفية',
        'مطور الويب المتكامل', 'مهندس DevOps', 'عالم بيانات',
        'مصمم واجهة المستخدم', 'مدير منتجات', 'مهندس ضمان الجودة',
        'مدير أنظمة', 'مهندس تعلم آلي', 'مطور تطبيقات الجوال',
        'مدير قواعد البيانات', 'متخصص دعم فني', 'محلل أمن تكنولوجيا المعلومات'
    ]
    
    # Create sample jobs - English
    for i in range(25):
        posted_days_ago = random.randint(1, 60)
        job_title_index = random.randint(0, len(job_titles) - 1)
        
        experience_text = ""
        if job_title_index < 5:  # Junior positions
            experience_text = "This is an entry-level position. 0-2 years of experience required."
        elif job_title_index < 10:  # Mid-level positions
            experience_text = "Looking for mid-level candidates with 2-5 years of experience."
        else:  # Senior positions
            experience_text = "Senior position requiring 5+ years of experience in the field."
        
        job = Job()
        job.title = job_titles[job_title_index]
        job.company = random.choice(companies)
        job.location = random.choice(locations)
        job.job_type = random.choice(job_types)
        job.salary_range = random.choice(salary_ranges)
        job.is_arabic = False
        job.posted_at = datetime.utcnow() - timedelta(days=posted_days_ago)
        
        job.description = f"""
        {job.company} is looking for a talented {job.title} to join our growing team. 
        This is a {job.job_type} position based in {job.location}.
        
        About the role:
        As a {job.title}, you will be responsible for designing, developing, and maintaining 
        software solutions that meet our clients' needs. You will collaborate with cross-functional 
        teams to create high-quality applications and services.
        
        Salary Range: {job.salary_range}
        """
        
        job.requirements = f"""
        Requirements:
        - {experience_text}
        - Bachelor's degree in Computer Science, Engineering, or related field
        - Proficiency in relevant programming languages
        - Strong problem-solving skills
        - Excellent communication and teamwork abilities
        - Experience with agile development methodologies
        """
        
        db.session.add(job)
    
    # Create sample jobs - Arabic
    for i in range(10):
        posted_days_ago = random.randint(1, 60)
        job_title_index = random.randint(0, len(arabic_job_titles) - 1)
        
        experience_text_ar = ""
        if job_title_index < 5:  # Junior positions
            experience_text_ar = "هذه وظيفة للمبتدئين. مطلوب خبرة من 0-2 سنوات."
        elif job_title_index < 10:  # Mid-level positions
            experience_text_ar = "نبحث عن مرشحين ذوي مستوى متوسط بخبرة من 2-5 سنوات."
        else:  # Senior positions
            experience_text_ar = "منصب رفيع المستوى يتطلب خبرة 5+ سنوات في المجال."
        
        job = Job()
        job.title = arabic_job_titles[job_title_index]
        job.company = random.choice(companies)
        job.location = 'الرياض، السعودية' if random.random() < 0.5 else 'القاهرة، مصر'
        job.job_type = random.choice(job_types)
        job.salary_range = random.choice(salary_ranges)
        job.is_arabic = True
        job.posted_at = datetime.utcnow() - timedelta(days=posted_days_ago)
        
        job.description = f"""
        تبحث شركة {job.company} عن {job.title} موهوب للانضمام إلى فريقنا المتنامي.
        هذه وظيفة {job.job_type} مقرها {job.location}.
        
        عن الدور:
        بصفتك {job.title}، ستكون مسؤولاً عن تصميم وتطوير وصيانة
        حلول برمجية تلبي احتياجات عملائنا. ستتعاون مع فرق متعددة الوظائف
        لإنشاء تطبيقات وخدمات عالية الجودة.
        
        نطاق الراتب: {job.salary_range}
        """
        
        job.requirements = f"""
        المتطلبات:
        - {experience_text_ar}
        - بكالوريوس في علوم الكمبيوتر أو الهندسة أو مجال ذي صلة
        - إجادة لغات البرمجة ذات الصلة
        - مهارات قوية في حل المشكلات
        - مهارات ممتازة في التواصل والعمل الجماعي
        - خبرة في منهجيات التطوير المرنة
        """
        
        db.session.add(job)
    
    db.session.commit()
    
    print(f"Added {25 + 10} sample jobs")

def create_sample_scholarships():
    # Clear existing scholarships
    Scholarship.query.delete()
    
    # Organizations
    organizations = [
        'Harvard University', 'MIT', 'Stanford University', 'Oxford University',
        'Cambridge University', 'King Saud University', 'Cairo University',
        'Gates Foundation', 'Fulbright Program', 'DAAD', 'Chevening Scholarships'
    ]
    
    # Countries
    countries = ['US', 'UK', 'CA', 'AU', 'SA', 'AE', 'EG', 'JO', 'International']
    
    # Fields of study
    fields = [
        'Computer Science', 'Engineering', 'Medicine', 'Business Management',
        'Arts & Humanities', 'Science', 'Education', 'Law',
        'Social Sciences', 'Mathematics'
    ]
    
    # Scholarship titles
    scholarship_titles = [
        'Full Merit Scholarship', 'Academic Excellence Award', 'International Student Grant',
        'Graduate Research Scholarship', 'Professional Development Fund',
        'Women in STEM Scholarship', 'Global Leadership Award', 'Future Innovators Grant',
        'Emerging Talent Scholarship', 'Cross-Cultural Education Fund'
    ]
    
    arabic_scholarship_titles = [
        'منحة الاستحقاق الكاملة', 'جائزة التميز الأكاديمي', 'منحة الطلاب الدوليين',
        'منحة بحث للدراسات العليا', 'صندوق التطوير المهني',
        'منحة النساء في العلوم والتكنولوجيا', 'جائزة القيادة العالمية', 'منحة المبتكرين المستقبليين',
        'منحة المواهب الناشئة', 'صندوق التعليم متعدد الثقافات'
    ]
    
    # Funding amounts
    amounts = [
        'Full Tuition', '$10,000 per year', '$25,000 per year', 
        'Up to $50,000', 'Full Funding', 'Partial Tuition',
        '€15,000 per academic year', 'Monthly stipend + tuition waiver'
    ]
    
    # Create sample scholarships - English
    for i in range(20):
        days_until_deadline = random.randint(7, 365)
        posted_days_ago = random.randint(1, 90)
        
        scholarship = Scholarship()
        scholarship.title = random.choice(scholarship_titles)
        scholarship.organization = random.choice(organizations)
        scholarship.country = random.choice(countries)
        scholarship.field_of_study = random.choice(fields)
        scholarship.amount = random.choice(amounts)
        scholarship.is_arabic = False
        scholarship.deadline = datetime.utcnow() + timedelta(days=days_until_deadline)
        scholarship.posted_at = datetime.utcnow() - timedelta(days=posted_days_ago)
        
        scholarship.description = f"""
        {scholarship.organization} is pleased to announce the {scholarship.title} for students 
        in {scholarship.field_of_study}. This scholarship aims to support exceptional students 
        who demonstrate academic excellence and leadership potential.
        
        The scholarship provides {scholarship.amount} to help students pursue their studies 
        in {scholarship.country}.
        
        Application deadline: {scholarship.deadline.strftime('%B %d, %Y')}
        """
        
        scholarship.eligibility = f"""
        Eligibility requirements:
        - Bachelor's degree with minimum GPA of 3.0
        - Strong academic record in {scholarship.field_of_study}
        - Demonstrated leadership abilities
        - Proficiency in English
        - {'International students are welcome to apply' if random.random() < 0.7 else 'Limited to citizens of ' + scholarship.country}
        """
        
        db.session.add(scholarship)
    
    # Create sample scholarships - Arabic
    for i in range(10):
        days_until_deadline = random.randint(7, 365)
        posted_days_ago = random.randint(1, 90)
        
        scholarship = Scholarship()
        scholarship.title = random.choice(arabic_scholarship_titles)
        scholarship.organization = random.choice(organizations)
        scholarship.country = 'SA' if random.random() < 0.5 else 'EG'
        scholarship.field_of_study = random.choice(fields)
        scholarship.amount = random.choice(amounts)
        scholarship.is_arabic = True
        scholarship.deadline = datetime.utcnow() + timedelta(days=days_until_deadline)
        scholarship.posted_at = datetime.utcnow() - timedelta(days=posted_days_ago)
        
        scholarship.description = f"""
        يسر {scholarship.organization} أن تعلن عن {scholarship.title} للطلاب
        في مجال {scholarship.field_of_study}. تهدف هذه المنحة إلى دعم الطلاب المتميزين
        الذين يظهرون التفوق الأكاديمي والإمكانات القيادية.
        
        توفر المنحة {scholarship.amount} لمساعدة الطلاب على متابعة دراستهم
        في {scholarship.country}.
        
        الموعد النهائي للتقديم: {scholarship.deadline.strftime('%B %d, %Y')}
        """
        
        scholarship.eligibility = f"""
        متطلبات الأهلية:
        - درجة البكالوريوس بمعدل تراكمي لا يقل عن 3.0
        - سجل أكاديمي قوي في {scholarship.field_of_study}
        - إظهار قدرات قيادية
        - إتقان اللغة الإنجليزية
        - {'يُرحب بتقديم الطلاب الدوليين' if random.random() < 0.7 else 'مقتصرة على مواطني ' + scholarship.country}
        """
        
        db.session.add(scholarship)
    
    db.session.commit()
    
    print(f"Added {20 + 10} sample scholarships")

def create_document_templates():
    # Clear existing templates
    DocumentTemplate.query.delete()
    
    # CV Templates - English
    cv_template_1 = DocumentTemplate()
    cv_template_1.name = "Professional CV Template"
    cv_template_1.description = "A clean, professional CV layout suitable for corporate applications."
    cv_template_1.template_type = "cv"
    cv_template_1.is_arabic = False
    cv_template_1.template_content = """
    <div class="professional-template">
        <h1>{name}</h1>
        <p>{email} | {phone} | {location}</p>
        
        <h2>Professional Summary</h2>
        <p>{summary}</p>
        
        <h2>Work Experience</h2>
        <div>{work_experience}</div>
        
        <h2>Education</h2>
        <div>{education}</div>
        
        <h2>Skills</h2>
        <div>{skills}</div>
    </div>
    """
    
    cv_template_2 = DocumentTemplate()
    cv_template_2.name = "Creative CV Template"
    cv_template_2.description = "A modern, creative CV design perfect for design and creative fields."
    cv_template_2.template_type = "cv"
    cv_template_2.is_arabic = False
    cv_template_2.template_content = """
    <div class="creative-template">
        <header>
            <h1>{name}</h1>
            <p class="subtitle">{job_title}</p>
            <p>{email} | {phone} | {location}</p>
        </header>
        
        <section class="about">
            <h2>About Me</h2>
            <p>{summary}</p>
        </section>
        
        <section class="experience">
            <h2>Experience</h2>
            <div>{work_experience}</div>
        </section>
        
        <section class="education">
            <h2>Education</h2>
            <div>{education}</div>
        </section>
        
        <section class="skills">
            <h2>Skills & Expertise</h2>
            <div>{skills}</div>
        </section>
    </div>
    """
    
    # CV Templates - Arabic
    cv_template_arabic = DocumentTemplate()
    cv_template_arabic.name = "قالب السيرة الذاتية المهنية"
    cv_template_arabic.description = "تخطيط سيرة ذاتية مهني ونظيف مناسب للتطبيقات المؤسسية."
    cv_template_arabic.template_type = "cv"
    cv_template_arabic.is_arabic = True
    cv_template_arabic.template_content = """
    <div class="professional-template rtl">
        <h1>{name}</h1>
        <p>{email} | {phone} | {location}</p>
        
        <h2>ملخص مهني</h2>
        <p>{summary}</p>
        
        <h2>الخبرة العملية</h2>
        <div>{work_experience}</div>
        
        <h2>التعليم</h2>
        <div>{education}</div>
        
        <h2>المهارات</h2>
        <div>{skills}</div>
    </div>
    """
    
    # Cover Letter Templates - English
    cover_letter_template_1 = DocumentTemplate()
    cover_letter_template_1.name = "Standard Cover Letter"
    cover_letter_template_1.description = "A traditional, formal cover letter format suitable for most industries."
    cover_letter_template_1.template_type = "cover_letter"
    cover_letter_template_1.is_arabic = False
    cover_letter_template_1.template_content = """
    <div class="standard-cover-letter">
        <div class="sender-info">
            <p>{name}</p>
            <p>{email}</p>
            <p>{phone}</p>
            <p>{location}</p>
            <p>{date}</p>
        </div>
        
        <div class="recipient-info">
            <p>{recipient_name}</p>
            <p>{company_name}</p>
            <p>{company_address}</p>
        </div>
        
        <div class="salutation">
            <p>Dear {recipient_name},</p>
        </div>
        
        <div class="body">
            <p>{opening_paragraph}</p>
            <p>{body_paragraph}</p>
            <p>{closing_paragraph}</p>
        </div>
        
        <div class="signature">
            <p>Sincerely,</p>
            <p>{name}</p>
        </div>
    </div>
    """
    
    # Cover Letter Templates - Arabic
    cover_letter_template_arabic = DocumentTemplate()
    cover_letter_template_arabic.name = "خطاب تغطية قياسي"
    cover_letter_template_arabic.description = "تنسيق خطاب تغطية تقليدي ورسمي مناسب لمعظم الصناعات."
    cover_letter_template_arabic.template_type = "cover_letter"
    cover_letter_template_arabic.is_arabic = True
    cover_letter_template_arabic.template_content = """
    <div class="standard-cover-letter rtl">
        <div class="sender-info">
            <p>{name}</p>
            <p>{email}</p>
            <p>{phone}</p>
            <p>{location}</p>
            <p>{date}</p>
        </div>
        
        <div class="recipient-info">
            <p>{recipient_name}</p>
            <p>{company_name}</p>
            <p>{company_address}</p>
        </div>
        
        <div class="salutation">
            <p>عزيزي/عزيزتي {recipient_name}،</p>
        </div>
        
        <div class="body">
            <p>{opening_paragraph}</p>
            <p>{body_paragraph}</p>
            <p>{closing_paragraph}</p>
        </div>
        
        <div class="signature">
            <p>مع خالص التقدير،</p>
            <p>{name}</p>
        </div>
    </div>
    """
    
    db.session.add_all([
        cv_template_1, cv_template_2, cv_template_arabic,
        cover_letter_template_1, cover_letter_template_arabic
    ])
    
    db.session.commit()
    
    print("Added document templates")

if __name__ == "__main__":
    with app.app_context():
        print("Seeding the database with sample data...")
        create_sample_jobs()
        create_sample_scholarships()
        create_document_templates()
        print("Database seeding completed successfully!")