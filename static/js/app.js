document.addEventListener('DOMContentLoaded', function () {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach((element) => {
        setTimeout(() => {
            element.style.opacity = '0';
            element.style.transition = 'opacity 0.3s ease';
            setTimeout(() => element.remove(), 300);
        }, 2400);
    });

    document.querySelectorAll('.ajax-response-form').forEach((form) => {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            if (form.dataset.sending === 'true') return;

            const input = form.querySelector('input[name="message"]');
            const button = form.querySelector('button[type="submit"]');
            const feedback = form.querySelector('.response-feedback');
            if (!input || !button || !feedback) {
                form.submit();
                return;
            }

            const originalButtonText = button.textContent;
            const formData = new FormData(form);
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 15000);
            form.dataset.sending = 'true';
            button.disabled = true;
            button.textContent = 'Sending...';
            input.disabled = true;
            feedback.textContent = '';
            feedback.classList.remove('text-danger');

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: { Accept: 'application/json' },
                    body: formData,
                    signal: controller.signal,
                });
                let result;
                try {
                    result = await response.json();
                } catch {
                    throw new Error('The server returned an unreadable response. Please refresh and try again.');
                }
                if (!response.ok || !result.success) {
                    throw new Error(result.message || 'Could not send response.');
                }

                if (result.message.toLowerCase().includes('reopened')) {
                    window.location.reload();
                    return;
                }

                const entry = document.createElement('div');
                entry.className = 'response-entry';
                const author = document.createElement('strong');
                author.textContent = result.author_name;
                const details = document.createElement('small');
                details.textContent = ` ${result.author_role} · just now`;
                const message = document.createElement('div');
                message.textContent = input.value.trim();
                entry.append(author, details, document.createElement('br'), message);
                form.closest('.response-thread').insertBefore(entry, form);
                input.value = '';
                feedback.textContent = 'Response sent.';
            } catch (error) {
                feedback.textContent = error.name === 'AbortError'
                    ? 'The request timed out. Please try again.'
                    : error.message || 'Could not send response. Please try again.';
                feedback.classList.add('text-danger');
            } finally {
                clearTimeout(timeout);
                form.dataset.sending = 'false';
                button.disabled = false;
                button.textContent = originalButtonText;
                input.disabled = false;
            }
        });
    });
});
