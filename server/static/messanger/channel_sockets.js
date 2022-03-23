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
    let message = new Message(messageJson);
    if (message.channel.id === messageList.channel.id)
        showMessagesAppend([new Message(messageJson)]);
});