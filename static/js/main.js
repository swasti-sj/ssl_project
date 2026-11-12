document.addEventListener('DOMContentLoaded', function() {

    // auto-dismiss flash alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(function() { alert.remove(); }, 500);
        }, 5000);
    });

    // live search filtering on events page
    var searchInput = document.querySelector('.filter-form input[name="search"]');
    if (searchInput) {
        var debounceTimer;
        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            var query = this.value.toLowerCase();
            debounceTimer = setTimeout(function() {
                var cards = document.querySelectorAll('.event-card');
                cards.forEach(function(card) {
                    var title = card.querySelector('h3').textContent.toLowerCase();
                    var desc = card.querySelector('.event-desc');
                    var descText = desc ? desc.textContent.toLowerCase() : '';
                    if (title.indexOf(query) !== -1 || descText.indexOf(query) !== -1) {
                        card.style.display = '';
                    } else {
                        card.style.display = 'none';
                    }
                });
            }, 300);
        });
    }

    // form validation
    var forms = document.querySelectorAll('.form-card');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            var required = form.querySelectorAll('[required]');
            var valid = true;
            required.forEach(function(field) {
                if (!field.value.trim()) {
                    field.style.borderColor = '#e74c3c';
                    valid = false;
                } else {
                    field.style.borderColor = '#ddd';
                }
            });
            if (!valid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });

});
