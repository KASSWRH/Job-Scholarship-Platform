/**
 * HireScholar - Job & Scholarship Search Platform
 * RTL Support JavaScript File
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check if the page should be in RTL mode
    const htmlElement = document.documentElement;
    const isRTL = htmlElement.getAttribute('dir') === 'rtl';
    
    if (isRTL) {
        // Fix input group button positions in RTL
        const inputGroups = document.querySelectorAll('.input-group');
        inputGroups.forEach(group => {
            const buttons = group.querySelectorAll('.input-group-text');
            buttons.forEach(button => {
                // Swap bootstrap classes for correct RTL positioning
                if (button.classList.contains('rounded-end')) {
                    button.classList.remove('rounded-end');
                    button.classList.add('rounded-start');
                }
            });
            
            const inputs = group.querySelectorAll('.form-control');
            inputs.forEach(input => {
                if (input.classList.contains('rounded-start')) {
                    input.classList.remove('rounded-start');
                    input.classList.add('rounded-end');
                }
            });
        });
        
        // Adjust float classes for RTL
        const floatEnd = document.querySelectorAll('.float-end');
        floatEnd.forEach(el => {
            el.classList.remove('float-end');
            el.classList.add('float-start');
        });
        
        const floatStart = document.querySelectorAll('.float-start:not(.float-end-original)');
        floatStart.forEach(el => {
            if (!el.classList.contains('float-start-original')) {
                el.classList.add('float-end-original');
                el.classList.remove('float-start');
                el.classList.add('float-end');
            }
        });
        
        // Adjust text alignment classes for RTL
        const textEnd = document.querySelectorAll('.text-end');
        textEnd.forEach(el => {
            el.classList.remove('text-end');
            el.classList.add('text-start');
        });
        
        const textStart = document.querySelectorAll('.text-start:not(.text-end-original)');
        textStart.forEach(el => {
            if (!el.classList.contains('text-start-original')) {
                el.classList.add('text-end-original');
                el.classList.remove('text-start');
                el.classList.add('text-end');
            }
        });
        
        // Fix dropdown menus for RTL
        const dropdownMenus = document.querySelectorAll('.dropdown-menu');
        dropdownMenus.forEach(menu => {
            if (menu.classList.contains('dropdown-menu-end')) {
                menu.classList.remove('dropdown-menu-end');
            } else {
                menu.classList.add('dropdown-menu-end');
            }
        });
        
        // Adjust card layouts if needed
        const cardLayouts = document.querySelectorAll('.card-layout');
        cardLayouts.forEach(card => {
            const cardImage = card.querySelector('.card-img-start');
            if (cardImage) {
                cardImage.classList.remove('card-img-start');
                cardImage.classList.add('card-img-end');
            }
        });
        
        // Fix form check alignment for RTL
        const formChecks = document.querySelectorAll('.form-check');
        formChecks.forEach(check => {
            if (!check.classList.contains('form-check-rtl-fixed')) {
                check.classList.add('form-check-rtl-fixed');
                const input = check.querySelector('.form-check-input');
                const label = check.querySelector('.form-check-label');
                
                if (input && label) {
                    // Adjust the margin
                    input.style.marginRight = '0';
                    input.style.marginLeft = '0.5em';
                }
            }
        });
        
        // Fix back to top button position for RTL
        const backToTopButton = document.getElementById('back-to-top');
        if (backToTopButton) {
            backToTopButton.style.right = 'auto';
            backToTopButton.style.left = '20px';
        }
    }
    
    // Handle language switcher for dynamic language changes
    const languageSwitchers = document.querySelectorAll('a[href*="set_language"]');
    languageSwitchers.forEach(switcher => {
        switcher.addEventListener('click', function(e) {
            // Allow the normal navigation to happen, this is just for visual feedback
            const langParam = this.getAttribute('href').split('/').pop();
            
            // Highlight the selected language
            languageSwitchers.forEach(ls => {
                ls.classList.remove('active');
            });
            this.classList.add('active');
        });
    });
    
    // Handle direction-aware elements that may need special attention in RTL
    const directionAwareElements = document.querySelectorAll('[data-direction-aware]');
    directionAwareElements.forEach(element => {
        if (isRTL) {
            // Apply specific RTL styling or class changes
            const rtlClass = element.getAttribute('data-rtl-class');
            if (rtlClass) {
                element.classList.add(rtlClass);
            }
            
            const rtlStyle = element.getAttribute('data-rtl-style');
            if (rtlStyle) {
                const styles = rtlStyle.split(';');
                styles.forEach(style => {
                    if (style.trim()) {
                        const [property, value] = style.split(':');
                        element.style[property.trim()] = value.trim();
                    }
                });
            }
        }
    });
});
