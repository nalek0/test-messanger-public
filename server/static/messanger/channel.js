class MessageList {
	_loading = false;

	isShouldLoadPreviousPage() {
		return !this._loading && this.pages[0].page !== 0;
	}

	async loadPreviousPage() {
		if (this.isShouldLoadPreviousPage()) {
			this._loading = true;

			let page = this.pages[0].page;
			let messages = Message.fetchMessages(CHANNEL_ID, page);
			let messageList = new MessageList(page, messages);
			this.pages.splice(0, 0, ...messageList.pages);
			
			this._loading = false;

			return messageList;
		}
		else
			return null;
	}

	sendMessage(text) {
		return Message.sendMessage(CHANNEL_ID, text);
	}

	constructor(lastMessagePage) {
		this.pages = [lastMessagePage];
		this.channel = new Channel(lastMessagePage.channel);
	}

	static loadLastMessages() {
		return Message.fetchMessages(CHANNEL_ID)
			.then( messagePage => new MessageList(messagePage) );
	}
}

var messageList = null;
let messagesWindow = null;

function messageToNodeConverFunction(message) {

	let author_node = document.createElement("a");
	author_node.classList.add("author");
	author_node.classList.add("link");
	author_node.textContent = message.author.first_name + " " + message.author.last_name;
	author_node.href = message.author.profile_url;

	let message_text_node = document.createElement("div");
	message_text_node.classList.add("paragraph");
	message_text_node.classList.add("message_text");
	message_text_node.textContent = message.text;

	let avatar_node = document.createElement("div");
	avatar_node.classList.add("avatar");
	avatar_node.style.backgroundImage = `url(${message.author.avatar.small})`;
	avatar_node.onclick = () => { window.location.href = message.author.profile_url; };

	let content_node = document.createElement("div");
	content_node.classList.add("content");
	content_node.appendChild(avatar_node);
	content_node.appendChild(message_text_node);

	let message_node = document.createElement('div');
	message_node.classList.add("message");
	message_node.appendChild(author_node);
	message_node.appendChild(content_node);
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
	messagesWindow.prepend(...messages.map(messageToNodeConverFunction));
}

function isScrolledUp() {
	return messagesWindow.scrollTop < 50;
}

function isScrolledDown() {
	return (messagesWindow.scrollTop + messagesWindow.clientHeight === messagesWindow.scrollHeight);
}

function scrollDown() {
	messagesWindow.scrollTop = messagesWindow.scrollHeight - messagesWindow.clientHeight;
}

function showMessagesAppend(messages) {
	let shouldScrollDown = isScrolledDown();

	messagesWindow.append(...messages.map(messageToNodeConverFunction));
	if (shouldScrollDown)
		scrollDown();
}

async function loadLastMessages() {
	messageList = await MessageList.loadLastMessages();
	showMessagesPrepend(messageList.pages.flatMap( page => page.messages ));
}

async function messagesOnScrollEvent() {
	if (isScrolledUp()) {
		let messagesList = await messageList.loadPreviousPage();
		if (messagesList)
			showMessagesPrepend(messagesList.pages.flatMap( page => page.messages ));
	}
}

window.onload = async () => {
	messagesWindow = document.getElementById("messages_window");
	messagesWindow.onscroll = messagesOnScrollEvent;
	await loadLastMessages();
	scrollDown();
};