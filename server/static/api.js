class User {
	constructor(data) {
        this.id = data.id;
        this.first_name = data.first_name;
        this.last_name = data.last_name;
        this.username = data.username;
        this.description = data.description;
	}
}

class Channel {
	constructor(data) {
		this.id = data.id;
	}
}

class Message {
	constructor(data) {
        this.id = data.id;
        this.text = data.text;
        this.datetime = Date.parse(data.datetime);
        this.channel = new Channel(data.channel);
        this.author = new User(data.author);
	}
}

class MessageList {
	sendMessage(text) {
		let messageData = {
			"channel_id": this.channel.id,
			"text": text
		};
		return makeRequest(
			"POST",
			"/api/channel/send_message",
			messageData
		).then(value => new Message(JSON.parse(value)["data"]));
	}

	constructor(data) {
		this.messages = [];
		for (let messageData of data.messages)
			this.messages.push(new Message(messageData));
		this.channel = new Channel(data.channel);

		this.isAllMessagesLoaded = this.messages.length == 0;
	}

	static loadMessages() {
		let requestPromise = makeRequest("POST", "/api/channel/load_messages", { "channel_id": CHANNEL_ID });

	    return requestPromise.then(value => {
			let data = JSON.parse(value)["data"];
			return new MessageList(data);
		});
	}
}

function makeRequest(method, url, data = {}) {
    return new Promise((resolve, reject) => {
        let xhr = new XMLHttpRequest();
        xhr.open(method, url);
		xhr.setRequestHeader("Content-Type", "application/json; charset=utf-8");
        
        xhr.onload = function () {
            if (this.status >= 200 && this.status < 300) {
                resolve(xhr.response);
            } else {
                reject({
                    status: this.status,
                    statusText: xhr.statusText
                });
            }
        };

        xhr.onerror = function () {
            reject({
                status: this.status,
                statusText: xhr.statusText
            });
        };
        
        xhr.send(JSON.stringify(data));
    });
}