// Дістаємо CSRF-токен (Django вимагає його для безпеки при POST-запитах)
        function getCookie(name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
        }
        const csrftoken = getCookie('csrftoken');

        const chat = document.getElementById('chat');
        const form = document.getElementById('chat-form');
        const input = document.getElementById('message');
        const sendBtn = document.getElementById('send-btn');

        // Додає бульбашку повідомлення на сторінку
        function addMessage(role, text) {
            const div = document.createElement('div');
            div.className = 'msg ' + role;
            div.textContent = text;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight; // прокрутка вниз
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const text = input.value.trim();
            if (!text) return;

            addMessage('user', text);   // одразу показуємо повідомлення користувача
            input.value = '';
            sendBtn.disabled = true;
            sendBtn.textContent = '...';

            try {
                const res = await fetch('/send/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrftoken,
                    },
                    body: 'message=' + encodeURIComponent(text),
                });
                const data = await res.json();
                if (data.reply) {
                    addMessage('assistant', data.reply);
                } else {
                    addMessage('assistant', '' + (data.error || 'Error'));
                }
            } catch (err) {
                addMessage('assistant', 'Connection error');
            } finally {
                sendBtn.disabled = false;
                sendBtn.textContent = 'Send';
                input.focus();
            }
        });

        // Очищення історії
        document.getElementById('clear').addEventListener('click', async () => {
            await fetch('/clear/', {
                method: 'POST',
                headers: { 'X-CSRFToken': csrftoken },
            });
            chat.innerHTML = '';
        });

        // Прокрутка вниз при завантаженні (якщо вже є історія)
        chat.scrollTop = chat.scrollHeight;