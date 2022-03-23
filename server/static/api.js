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

class Client extends User {
	static _instance = null;
	static _loading = false;


	constructor(data) {
		super(data);
		this.friends = data.friends.map(friendData => new User(friendData));
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

// Permission codes:
var WATCH_CHANNEL_INFO = 0
var READ_CHANNEL = 1
var WATCH_CHANNEL_MEMBERS = 2
var SEND_MESSAGES = 3
var EDIT_CHANNEL = 4
var DELETE_CHANNEL = 5

class ChannelPermission {
	constructor(data) {
		this.user = new User(data.user);
		this.permissionCode = data.permission_code;
	}
}

class UserPermission {
	constructor(user, channel, channelPermissions) {
		this.user = user;
		this.channel = channel;
		this.channelPermissions = channelPermissions;
	}

	hasPermission(permissionCode) {
		return this.channelPermissions.some( it => it.permissionCode === permissionCode );
	}
}

class Channel {
	constructor(data) {
		this.id = data.id;
		this.members = data.members.map( it => new User(it) );
		this.permissions = data.permissions.map( it => new ChannelPermission(it) );
	}

	getAdmins() {
		return this.members.filter( member => this.getUserPermission(member).hasPermission(DELETE_CHANNEL) );
	}

	getModerators() {
		return this.members.filter( member => this.getUserPermission(member).hasPermission(EDIT_CHANNEL) );
	}

	getMembers() {
		return this.members;
	}

	getUserPermission(user) {
        return new UserPermission(user, this, this.permissions.filter( it => it.user.id === user.id ));
	}

	static getChannel(channel_id) {
		return makeRequest(
			"POST",
			"/api/channel/get_channel",
			{ "channel_id": channel_id }
		).then(response => new Channel(JSON.parse(response)));
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
