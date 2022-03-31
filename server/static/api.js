class User {
	constructor(data) {
        this.id = data.id;
        this.first_name = data.first_name;
        this.last_name = data.last_name;
        this.username = data.username;
        this.description = data.description;
	}

	getFullName() {
		return `${this.first_name} ${this.last_name}`;
	}

	getProfileURL() {
		return `/profile/${this.username}`;
	}

	getLinkNode() {
		let linkNode = document.createElement("a");
		linkNode.href = this.getProfileURL();
		linkNode.classList.add("link");
		linkNode.textContent = this.getFullName();
		return linkNode;
	}

	static getUser(user_id) {
		return makeRequest(
			"POST",
			"/api/user/get_user",
			{ "user_id": user_id }
		).then(response => new User(JSON.parse(response)));
	}
}

class ChannelRole {
	constructor(data) {
		this.id = data.id;
		this.role_name = data.role_name;
		this.watch_channel_information_permission = data.watch_channel_information_permission;
		this.watch_channel_members_permission = data.watch_channel_members_permission;
		this.read_channel_permission = data.read_channel_permission;
		this.send_messages_permission = data.send_messages_permission;
		this.edit_channel_permission = data.edit_channel_permission;
	}
}

class UserRole {
	constructor(data) {
		this.id = data.id;
		this.user = new User(data.user);
		this.role = new ChannelRole(data.role);
		this.channel = new Channel(data.channel);
	}
}

class ChannelMember {
	constructor(data) {
		this.id = data.id;
		this.user = new User(data.user);
		this.channel = new Channel(data.channel);
		this.user_roles = data.user_roles.map( it => new UserRole(it) );
	}
}

class Channel {
	constructor(data) {
		this.id = data.id;
		this.title = data.title;
		this.description = data.description;
		this.roles = data.roles.map( it => new ChannelRole(it) );
	}

	updateChannelData(data) {
		return makeRequest(
			"POST",
			"/api/channel/update_channel",
			data
		);
	}

	getAdmins() {
		return this.members.filter( member => this.getUserPermission(member).hasPermission(DELETE_CHANNEL) );
	}

	getModerators() {
		return this.members.filter( member => this.getUserPermission(member).hasPermission(EDIT_CHANNEL) );
	}

	getMember(user) {
		return this.members;
	}

	static getChannel(channel_id) {
		return makeRequest(
			"POST",
			"/api/channel/get_channel",
			{ "channel_id": channel_id }
		).then(response => new Channel(JSON.parse(response)));
	}
}

class Client extends User {
	constructor(data) {
		super(data);
		this.friends = data.friends.map(friendData => new User(friendData));
		this.channels = data.channels.map(channelData => new Channel(channelData));
	}

	isFriend(user) {
		return this.friends.some(it => it.id === user.id);
	}

	addFriend(user) {
		return makeRequest(
			"POST",
			"/api/user/add_friend",
			{ "user_id": user.id }
		);
	}

	removeFriend(user) {
		return makeRequest(
			"POST",
			"/api/user/remove_friend",
			{ "user_id": user.id }
		);
	}

	static getClient() {
		return makeRequest(
			"POST",
			"/api/user/get_client_user"
		).then(response => {
			if (response === null)
				return null;
			else
				return new Client(JSON.parse(response));
		});
	}

	static updateClientData(data) {
		return makeRequest(
			"POST",
			"/api/user/update_profile",
			data
		);
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

class MessagePage {
	constructor(data) {
		this.page = data.page;
		this.messages = data.messages;
	}	
}

class MessageList {
	_loading = false;

	isShouldLoadPreviousPage() {
		return !this._loading && this.pages[0].page !== 0;
	}

	async loadPreviousPage() {
		if (this.isShouldLoadPreviousPage()) {
			this._loading = true;

			let messagePageData = await makeRequest("POST", "/api/channel/load_messages", { "channel_id": CHANNEL_ID, "page": this.pages[0].page - 1 });
			let messageList = new MessageList(JSON.parse(messagePageData)["data"]);
			this.pages.splice(0, 0, ...messageList.pages);
			
			this._loading = false;

			return messageList;
		}
		else
			return null;
	}

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
		this.pages = [];
		for (let pageData of data.pages)
			this.pages.push(new MessagePage(pageData));
		this.channel = new Channel(data.channel);
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
