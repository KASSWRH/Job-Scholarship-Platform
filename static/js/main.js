/**
 * HireScholar - Job & Scholarship Search Platform
 * Main JavaScript File
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Initialize popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Handle notification badge updates
    function updateNotificationCount() {
        const notificationBadge = document.getElementById('notification-count');
        if (notificationBadge) {
            const unreadCount = parseInt(notificationBadge.textContent);
            if (unreadCount === 0) {
                notificationBadge.style.display = 'none';
            } else {
                notificationBadge.style.display = 'inline-block';
            }
        }
    }
    
    // Call the notification update function
    updateNotificationCount();
    
    // Handle mark as read buttons for notifications
    const markReadButtons = document.querySelectorAll('.mark-read-btn');
    markReadButtons.forEach(button => {
        button.addEventListener('click', function() {
            const notificationId = this.getAttribute('data-notification-id');
            markNotificationAsRead(notificationId);
        });
    });
    
    // Function to mark a notification as read
    function markNotificationAsRead(notificationId) {
        fetch(`/mark_notification_read/${notificationId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Find the notification element
                const notificationElement = document.querySelector(`.list-group-item[data-notification-id="${notificationId}"]`);
                if (notificationElement) {
                    // Update the notification styling
                    notificationElement.classList.remove('unread');
                    const titleElement = notificationElement.querySelector('h5');
                    if (titleElement) {
                        titleElement.classList.remove('fw-bold');
                    }
                    
                    // Remove the mark as read button
                    const readButton = notificationElement.querySelector('.mark-read-btn');
                    if (readButton) {
                        readButton.remove();
                    }
                }
                
                // Update the notification count in the navbar
                const notificationBadge = document.getElementById('notification-count');
                if (notificationBadge) {
                    const currentCount = parseInt(notificationBadge.textContent);
                    if (currentCount > 1) {
                        notificationBadge.textContent = currentCount - 1;
                    } else {
                        notificationBadge.textContent = '';
                        notificationBadge.style.display = 'none';
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error marking notification as read:', error);
        });
    }
    
    // Job Search Form Enhancements
    const jobSearchForm = document.querySelector('form[action="/jobs"]');
    if (jobSearchForm) {
        const searchInput = jobSearchForm.querySelector('input[name="search"]');
        if (searchInput) {
            // Add clear button functionality
            searchInput.addEventListener('input', function() {
                const clearButton = this.parentNode.querySelector('.clear-search');
                if (this.value && !clearButton) {
                    // Create clear button if it doesn't exist
                    const btn = document.createElement('button');
                    btn.className = 'clear-search btn btn-sm btn-link position-absolute end-0 top-50 translate-middle-y text-muted';
                    btn.innerHTML = '<i class="fa-solid fa-times"></i>';
                    btn.type = 'button';
                    btn.style.zIndex = '5';
                    btn.addEventListener('click', () => {
                        this.value = '';
                        btn.remove();
                        // Optional: auto-submit the form when cleared
                        // jobSearchForm.submit();
                    });
                    this.parentNode.style.position = 'relative';
                    this.parentNode.appendChild(btn);
                } else if (!this.value && clearButton) {
                    clearButton.remove();
                }
            });
        }
    }
    
    // Scholarship Search Form Enhancements
    const scholarshipSearchForm = document.querySelector('form[action="/scholarships"]');
    if (scholarshipSearchForm) {
        const searchInput = scholarshipSearchForm.querySelector('input[name="search"]');
        if (searchInput) {
            // Add clear button functionality (same as job search)
            searchInput.addEventListener('input', function() {
                const clearButton = this.parentNode.querySelector('.clear-search');
                if (this.value && !clearButton) {
                    const btn = document.createElement('button');
                    btn.className = 'clear-search btn btn-sm btn-link position-absolute end-0 top-50 translate-middle-y text-muted';
                    btn.innerHTML = '<i class="fa-solid fa-times"></i>';
                    btn.type = 'button';
                    btn.style.zIndex = '5';
                    btn.addEventListener('click', () => {
                        this.value = '';
                        btn.remove();
                    });
                    this.parentNode.style.position = 'relative';
                    this.parentNode.appendChild(btn);
                } else if (!this.value && clearButton) {
                    clearButton.remove();
                }
            });
        }
    }
    
    // File Upload Preview
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name;
            const fileSize = e.target.files[0]?.size / 1024 / 1024; // Convert to MB
            const fileHelp = document.getElementById('fileHelp');
            
            if (fileName && fileHelp) {
                // Check if the user's language is Arabic
                const isArabic = document.documentElement.lang === 'ar';
                if (isArabic) {
                    fileHelp.textContent = `الملف المختار: ${fileName} (${fileSize.toFixed(2)} ميجابايت)`;
                } else {
                    fileHelp.textContent = `Selected file: ${fileName} (${fileSize.toFixed(2)} MB)`;
                }
            }
        });
    }
    
    // Back to top button
    const backToTopButton = document.createElement('button');
    backToTopButton.id = 'back-to-top';
    backToTopButton.className = 'btn btn-primary rounded-circle position-fixed';
    backToTopButton.innerHTML = '<i class="fa-solid fa-arrow-up"></i>';
    backToTopButton.style.bottom = '20px';
    backToTopButton.style.right = '20px';
    backToTopButton.style.display = 'none';
    backToTopButton.style.width = '40px';
    backToTopButton.style.height = '40px';
    backToTopButton.style.zIndex = '1000';
    document.body.appendChild(backToTopButton);
    
    // Show back to top button when scrolling down
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopButton.style.display = 'block';
        } else {
            backToTopButton.style.display = 'none';
        }
    });
    
    // Scroll to top when clicking the button
    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // Handle document type selection in upload form
    const documentTypeSelect = document.getElementById('document_type');
    const documentTitleInput = document.getElementById('title');
    
    if (documentTypeSelect && documentTitleInput) {
        documentTypeSelect.addEventListener('change', function() {
            const selectedType = this.value;
            // Add appropriate prefix to title based on document type if empty
            if (!documentTitleInput.value || documentTitleInput.value.startsWith('CV - ') || 
                documentTitleInput.value.startsWith('Cover Letter - ') || documentTitleInput.value.startsWith('Document - ')) {
                
                const isArabic = document.documentElement.lang === 'ar';
                
                if (selectedType === 'cv') {
                    documentTitleInput.value = isArabic ? 'السيرة الذاتية - ' : 'CV - ';
                } else if (selectedType === 'cover_letter') {
                    documentTitleInput.value = isArabic ? 'خطاب التغطية - ' : 'Cover Letter - ';
                } else {
                    documentTitleInput.value = isArabic ? 'وثيقة - ' : 'Document - ';
                }
            }
        });
    }
});
