import io from 'socket.io-client'

const messages = [];

function renderMessages(message) {
    const messageBox = document.querySelector('.chat__box');
    let newBox = document.createElement('div');
    newBox.classList = 'chat__message message box';
    newBox.innerHTML = `<span class="has-text-info">${message.name}</span> ${message.message}`;
    messageBox.appendChild(newBox)
}

let socket = null;
document.querySelector('#enter').addEventListener('click', (e) => {
    e.preventDefault();
    const user_name = document.querySelector('#username').value;
    socket = io('http://localhost:3000/chat', {query: {name: user_name}});
    socket.on('connect', () => console.log('Подключено'));
    socket.on('disconnect', () => console.log('Успешно отключено'));
    socket.on('reply', (data) => renderMessages(data));
    document.querySelector('.chat_box-modal').classList.add('hide');

    document.querySelector('#sendForm').addEventListener('click', (e) => {
        e.preventDefault();
        const message = document.querySelector('#message').value;
        socket.emit('chat message', message, () => {
            renderMessages({name: user_name, message: message})
        })
    });
});

