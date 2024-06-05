
document.addEventListener('DOMContentLoaded', function() {
    
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            
            event.preventDefault();
            
            
            const inputs = form.querySelectorAll('input');
            let valid = true;
            inputs.forEach(input => {
                if (input.value.trim() === '') {
                    valid = false;
                    input.classList.add('is-invalid');
                } else {
                    input.classList.remove('is-invalid');
                }
            });
            
            
            if (valid) {
                form.submit();
            }
        });
    });
    
    
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            if (input.value.trim() !== '') {
                input.classList.remove('is-invalid');
            }
        });
    });
});
