socketio.on('connect', () => {
    console.log("Connected");
});

socketio.on('disconnect', () => {
    console.log("Disconnected");
});

socketio.on("channel_message", messageJson => {
    showMessagesAppend([new Message(messageJson)]);
});