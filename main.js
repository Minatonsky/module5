console.log('Hello world!')

const ws = new WebSocket('ws://localhost:8080')

formChat.addEventListener('submit', (e) => {
    e.preventDefault();
    const inputText = textField.value.trim();

    if (inputText.startsWith('exchange')) {
        const match = inputText.match(/exchange (\d+)/);
        const days = match ? parseInt(match[1]) : 1;
        
        if (days > 10) {
            alert("Error: Number of days should not exceed 10.");
            return;
        }

        ws.send(JSON.stringify({ command: 'exchange', args: { days } }));
    } else {
        ws.send(JSON.stringify({ command: 'message', text: inputText }));
    }

    textField.value = null;
});

ws.onopen = (e) => {
    console.log('Hello WebSocket!')
}

ws.onmessage = (e) => {
    console.log(e.data)
    text = e.data

    const elMsg = document.createElement('div')
    elMsg.textContent = text
    subscribe.appendChild(elMsg)
};
