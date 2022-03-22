class PushMessage {
	static timeToFading = 3000;

	constructor(text, type) {
		this.text = text;
		this.type = type;

		this.node = document.createElement("div");
		this.node.classList.add("push_message");
		this.node.classList.add(type);
		this.node.textContent = this.text;
	}

	runFading() {
		setTimeout(() => {
			this.node.classList.add("faded")
		}, PushMessage.timeToFading);
	}
}

class PushMessagesList {
	constructor() {
		this.pushMessages = [];
		
		this.node = document.createElement("div");
		this.node.classList.add("push_messages_floating_window");
	}

	addMessage(pushMessage) {
		this.pushMessages.push(pushMessage);
		this.node.appendChild(pushMessage.node);
		pushMessage.runFading()
	}
}

//    <div class="push_messages_window" id="push_messages_window"></div>

const pushMessagesList = new PushMessagesList();

window.onload = () => {
	document.getElementById("push_messages_window").appendChild(pushMessagesList.node);
};
