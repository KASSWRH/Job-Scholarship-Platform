/**
 * HireScholar - Job & Scholarship Search Platform
 * Document Generator JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Function to generate placeholder content based on form fields
    function generatePlaceholders() {
        // Get document type
        const templateType = document.querySelector('h1')?.textContent.includes('CV') ? 'cv' : 'cover_letter';
        
        // Document title field
        const titleInput = document.getElementById('title');
        if (titleInput && !titleInput.value) {
            const isArabic = document.documentElement.lang === 'ar';
            if (templateType === 'cv') {
                titleInput.value = isArabic ? 'السيرة الذاتية الاحترافية' : 'Professional CV';
            } else {
                titleInput.value = isArabic ? 'خطاب تغطية احترافي' : 'Professional Cover Letter';
            }
        }
        
        // Name field - try to use current user's name if empty
        const nameInput = document.getElementById('name');
        if (nameInput && !nameInput.value) {
            // Default already set in the template from current_user
        }
        
        // Example placeholders for CV
        if (templateType === 'cv') {
            const summaryInput = document.getElementById('summary');
            if (summaryInput && !summaryInput.value) {
                const isArabic = document.documentElement.lang === 'ar';
                
                if (isArabic) {
                    summaryInput.placeholder = 'مثال: محترف متمرس مع خبرة 5 سنوات في تطوير البرمجيات وإدارة المشاريع. خبرة في تقديم حلول مبتكرة وتحسين العمليات.';
                } else {
                    summaryInput.placeholder = 'Example: Seasoned professional with 5 years of experience in software development and project management. Skilled in delivering innovative solutions and optimizing processes.';
                }
            }
            
            const educationInput = document.getElementById('education');
            if (educationInput && !educationInput.value) {
                const isArabic = document.documentElement.lang === 'ar';
                
                if (isArabic) {
                    educationInput.placeholder = 'مثال:\nجامعة القاهرة، بكالوريوس في هندسة البرمجيات، 2018\nجامعة الإسكندرية، ماجستير في علوم الحاسب، 2020';
                } else {
                    educationInput.placeholder = 'Example:\nUniversity of Technology, Bachelor of Computer Science, 2018\nNational Institute of Technology, Master of Software Engineering, 2020';
                }
            }
            
            const experienceInput = document.getElementById('experience');
            if (experienceInput && !experienceInput.value) {
                const isArabic = document.documentElement.lang === 'ar';
                
                if (isArabic) {
                    experienceInput.placeholder = 'مثال:\nشركة تكنولوجيا المستقبل، مطور برمجيات، 2018-2020\n- تطوير تطبيقات الويب باستخدام React وNode.js\n- تحسين أداء التطبيقات بنسبة 40%\n\nشركة التقنية المتقدمة، مهندس برمجيات أول، 2020-الحاضر\n- قيادة فريق من 5 مطورين\n- تنفيذ مشاريع كبيرة للعملاء الرئيسيين';
                } else {
                    experienceInput.placeholder = 'Example:\nFuture Tech Inc., Software Developer, 2018-2020\n- Developed web applications using React and Node.js\n- Improved application performance by 40%\n\nAdvanced Technology Corp., Senior Software Engineer, 2020-Present\n- Led a team of 5 developers\n- Implemented major projects for key clients';
                }
            }
            
            const skillsInput = document.getElementById('skills');
            if (skillsInput && !skillsInput.value) {
                const isArabic = document.documentElement.lang === 'ar';
                
                if (isArabic) {
                    skillsInput.placeholder = 'مثال: تطوير الويب، جافا سكريبت، React، Node.js، بايثون، إدارة المشاريع، العمل الجماعي، حل المشكلات';
                } else {
                    skillsInput.placeholder = 'Example: Web Development, JavaScript, React, Node.js, Python, Project Management, Teamwork, Problem Solving';
                }
            }
        } 
        // Example placeholders for cover letter
        else if (templateType === 'cover_letter') {
            const companyInput = document.getElementById('company');
            if (companyInput && !companyInput.value) {
                companyInput.placeholder = 'ABC Corporation';
            }
            
            const positionInput = document.getElementById('position');
            if (positionInput && !positionInput.value) {
                positionInput.placeholder = 'Senior Software Engineer';
            }
            
            const introductionInput = document.getElementById('introduction');
            if (introductionInput && !introductionInput.value) {
                const isArabic = document.documentElement.lang === 'ar';
                
                if (isArabic) {
                    introductionInput.placeholder = 'مثال: أكتب للتعبير عن اهتمامي بمنصب مهندس البرمجيات الأول المعلن عنه على موقعكم. بصفتي محترف تقني ذو خبرة، أنا متحمس لفرصة الانضمام إلى فريقكم المتميز والمساهمة في مشاريعكم المبتكرة.';
                } else {
                    introductionInput.placeholder = 'Example: I am writing to express my interest in the Senior Software Engineer position advertised on your website. As an experienced tech professional, I am excited about the opportunity to join your outstanding team and contribute to your innovative projects.';
                }
            }
            
            const bodyInput = document.getElementById('body');
            if (bodyInput && !bodyInput.value) {
                const isArabic = document.documentElement.lang === 'ar';
                
                if (isArabic) {
                    bodyInput.placeholder = 'مثال: لدي أكثر من 5 سنوات من الخبرة في تطوير البرمجيات، مع التركيز على تطبيقات الويب وتطوير الواجهات الأمامية. في دوري الحالي، قمت بقيادة تطوير منصة تجارة إلكترونية تخدم أكثر من 50,000 مستخدم شهريًا، مما أدى إلى زيادة معدلات التحويل بنسبة 35%. خبرتي في JavaScript وReact وNode.js ستمكنني من إحداث تأثير فوري في مشاريعكم.';
                } else {
                    bodyInput.placeholder = 'Example: I have over 5 years of experience in software development, with a focus on web applications and frontend development. In my current role, I led the development of an e-commerce platform serving over 50,000 monthly users, resulting in a 35% increase in conversion rates. My expertise in JavaScript, React, and Node.js would enable me to make an immediate impact on your projects.';
                }
            }
            
            const conclusionInput = document.getElementById('conclusion');
            if (conclusionInput && !conclusionInput.value) {
                const isArabic = document.documentElement.lang === 'ar';
                
                if (isArabic) {
                    conclusionInput.placeholder = 'مثال: أشكركم على اهتمامكم بطلبي وأتطلع إلى مناقشة كيف يمكنني المساهمة في نجاح فريقكم. أنا متاح للمقابلة في أي وقت مناسب لكم.';
                } else {
                    conclusionInput.placeholder = 'Example: Thank you for considering my application. I look forward to discussing how I can contribute to your team\'s success. I am available for an interview at your convenience.';
                }
            }
        }
        
        // Setup form validation
        initFormValidation();
    }
    
    // Function to initialize form validation
    function initFormValidation() {
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', function(event) {
                // Check if any required field is empty
                const requiredFields = form.querySelectorAll('[required]');
                let hasEmptyFields = false;
                
                requiredFields.forEach(field => {
                    if (!field.value.trim()) {
                        hasEmptyFields = true;
                        field.classList.add('is-invalid');
                    } else {
                        field.classList.remove('is-invalid');
                    }
                });
                
                if (hasEmptyFields) {
                    event.preventDefault();
                    
                    // Show alert message
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
                    alertDiv.role = 'alert';
                    
                    const isArabic = document.documentElement.lang === 'ar';
                    alertDiv.textContent = isArabic ? 'يرجى ملء جميع الحقول المطلوبة.' : 'Please fill in all required fields.';
                    
                    const closeButton = document.createElement('button');
                    closeButton.type = 'button';
                    closeButton.className = 'btn-close';
                    closeButton.setAttribute('data-bs-dismiss', 'alert');
                    closeButton.setAttribute('aria-label', 'Close');
                    
                    alertDiv.appendChild(closeButton);
                    
                    // Add the alert at the top of the form
                    form.prepend(alertDiv);
                    
                    // Scroll to the first empty field
                    requiredFields.forEach(field => {
                        if (!field.value.trim()) {
                            field.focus();
                            
                            // Only focus the first empty field
                            return false;
                        }
                    });
                }
            });
            
            // Live validation when field loses focus
            const requiredFields = form.querySelectorAll('[required]');
            requiredFields.forEach(field => {
                field.addEventListener('blur', function() {
                    if (!this.value.trim()) {
                        this.classList.add('is-invalid');
                    } else {
                        this.classList.remove('is-invalid');
                    }
                });
                
                // Remove invalid class when typing
                field.addEventListener('input', function() {
                    if (this.value.trim()) {
                        this.classList.remove('is-invalid');
                    }
                });
            });
        }
    }
    
    // Function to add character count to textarea fields
    function addCharacterCounters() {
        const textareas = document.querySelectorAll('textarea');
        textareas.forEach(textarea => {
            // Create counter element
            const counter = document.createElement('div');
            counter.className = 'text-muted small text-end mt-1 character-counter';
            counter.textContent = `0/${textarea.maxLength || 'unlimited'}`;
            
            // Add counter after textarea
            textarea.parentNode.insertBefore(counter, textarea.nextSibling);
            
            // Update counter on input
            textarea.addEventListener('input', function() {
                counter.textContent = `${this.value.length}/${this.maxLength || 'unlimited'}`;
                
                // Change color when approaching limit
                if (this.maxLength && this.value.length > this.maxLength * 0.8) {
                    counter.classList.add('text-danger');
                } else {
                    counter.classList.remove('text-danger');
                }
            });
            
            // Initialize counter
            counter.textContent = `${textarea.value.length}/${textarea.maxLength || 'unlimited'}`;
        });
    }
    
    // Generate placeholders when page loads
    generatePlaceholders();
    
    // Add character counters for textareas if needed
    // Commented out as no maxLength is set on the textareas in the template
    // addCharacterCounters();
});
