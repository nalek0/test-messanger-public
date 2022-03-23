var socketsDiconnected = false;

socketio.on("connect", () => {
    if (socketsDiconnected) {
        socketsDiconnected = true;
        pushMessagesList.addMessage(new PushMessage("You are connected again", "ok_message"));
    }
});

socketio.on("disconnect", () => {
    socketsDiconnected = true;
    pushMessagesList.addMessage(new PushMessage("You are diconnected", "error"));
});

socketio.on("channel_message", messageJson => {
    showMessagesAppend([new Message(messageJson)]);
});