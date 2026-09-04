// Poputka AI - Client-side scripts

document.addEventListener('DOMContentLoaded', function() {
    // SOS confirmation
    const sosButtons = document.querySelectorAll('.btn-danger[data-sos]');
    sosButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            if (!confirm('ВНИМАНИЕ! Вы активируете экстренный сигнал SOS.\n\nВаши экстренные контакты получат уведомление с информацией о вашей поездке.\n\nПродолжить?')) {
                e.preventDefault();
            }
        });
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            }
        }, 5000);
    });

    // Auto-fill time from parsed text
    const timeInput = document.getElementById('desired_time');
    if (timeInput && !timeInput.value) {
        // Set default to next hour
        const now = new Date();
        now.setHours(now.getHours() + 1, 0, 0, 0);
        timeInput.value = now.toISOString().slice(0, 16);
    }

    // Validate URFU email on registration
    const emailInput = document.getElementById('email');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            const val = this.value.trim().toLowerCase();
            if (val && !val.endsWith('@stud.urfu.ru')) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            }
        });
    }
});
