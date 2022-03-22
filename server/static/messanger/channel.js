var messageList = null;

function messageToNodeConverFunction(message) {
	let message_node = document.createElement('div');
	message_node.classList.add("message");

	let author_node = document.createElement("div");
	author_node.classList.add("author");

	let message_text_node = document.createElement("div");
	message_text_node.classList.add("paragraph");
	message_text_node.classList.add("message_text");

	author_node.textContent = message.author.first_name + " " + message.author.last_name;
	message_text_node.textContent = message.text;

	message_node.appendChild(author_node);
	message_node.appendChild(message_text_node);
	return message_node;
}

async function sendMessage() {
	if (messageList == null)
		return;

	let textarea = document.getElementById("message_textarea");
	let text = textarea.value;
	textarea.value = "";

	await messageList.sendMessage(text);
}

function showMessagesPrepend(messages) {
	let messages_window = document.getElementById("messages_window");

	messages_window.prepend(...messages.map(messageToNodeConverFunction));
}

function showMessagesAppend(messages) {
	let messages_window = document.getElementById("messages_window");

	messages_window.append(...messages.map(messageToNodeConverFunction));
}

async function loadMessages() {
	messageList = await MessageList.loadMessages();
	showMessagesPrepend(messageList.messages);
}

window.onload = () => {
	loadMessages();
};