class User {
	constructor(data) {
        this.id = data.id;
        this.first_name 	= data.first_name;
        this.last_name 		= data.last_name;
        this.username 		= data.username;
        this.description 	= data.description;
        this.profile_url 	= data.profile_url;
	}

	getFullName() {
		return `${this.first_name} ${this.last_name}`;
	}

	getLinkNode() {
		let linkNode = document.createElement("a");
		linkNode.href = this.profile_url;
		linkNode.classList.add("link");
		linkNode.textContent = this.getFullName();
		return linkNode;
	}

	static getUser(user_id) {
		return makeAPIRequest(
			"/api/user/get",
			{ "user_id": user_id }
		).then(response => new User(JSON.parse(response)));
	}
}

class ChannelRole {
	constructor(data) {
		this.id = data.id;
		this.role_name = data.role_name;
		this.watch_channel_information_permission 	= data.watch_channel_information_permission;
		this.watch_channel_members_permission 		= data.watch_channel_members_permission;
		this.read_channel_permission 				= data.read_channel_permission;
		this.send_messages_permission 				= data.send_messages_permission;
		this.edit_channel_permission 				= data.edit_channel_permission;
	}
}

class UserRole {
	constructor(data) {
		this.id = data.id;
		this.user 		= new User(data.user);
		this.role 		= new ChannelRole(data.role);
		this.channel 	= new Channel(data.channel);
	}
}

class ChannelMember {
	constructor(data) {
		this.id = data.id;
		this.user 		= new User(data.user);
		this.channel 	= new Channel(data.channel);
		this.user_roles = data.user_roles.map( it => new UserRole(it) );
	}

	hasPermission(permissionName) {
		return this.user_roles.some( user_role => user_role.role[permissionName] );
	}
}

class Channel {
	constructor(data) {
		this.id = data.id;
		this.title 			= data.title;
		this.description 	= data.description;
		this.roles 			= data.roles.map( it => new ChannelRole(it) );
	}

	updateChannelData() {
		return makeAPIRequest(
			"/api/channel/update",
			{
				"channel_id": this.id,
				"title": this.title,
				"description": this.description
			}
		);
	}

	async getModerators(page=0, page_results=20) {
		return makeAPIRequest(
			"/api/channel/member/fetch",
			{ 
				"channel_id": this.id,
				"permissions": ["edit_channel_permission"],
				"page": page,
				"page_results": page_results
			}
		).then( response => JSON.parse(response)['data'].map ( it => new ChannelMember(it) ) );
	}

	async getMembers(page=0, page_results=20) {
		return makeAPIRequest(
			"/api/channel/member/fetch",
			{ 
				"channel_id": this.id,
				"permissions": [
					"watch_channel_information_permission", 
					"watch_channel_members_permission", 
					"read_channel_permission", 
					"send_messages_permission"
				],
				"page": page,
				"page_results": page_results
			}
		).then( response => JSON.parse(response)['data'].map ( it => new ChannelMember(it) ) );
	}

	getMember(user) {
		return makeAPIRequest(
			"/api/channel/member/get",
			{ 
				"channel_id": this.id, 
				"user_id": user.id 
			}
		).then( response => new ChannelMember(JSON.parse(response)) );
	}

	static getChannel(channel_id) {
		return makeAPIRequest(
			"/api/channel/get",
			{ "channel_id": channel_id }
		).then( response => new Channel(JSON.parse(response)) );
	}
}

class ChannelInvitation {
	constructor(data) {
		this.id = data.id;
		this.user 		= new User(data.user);
		this.channel 	= new Channel(data.channel);
	}

	static useInvitation(invitation_id) {
		return makeAPIRequest(
			"/api/channel/invitation/use",
			{ "invitation_id": invitation_id }
		);
	}

	static deleteInvitation(invitation_id) {
		return makeAPIRequest(
			"/api/channel/invitation/delete",
			{ "invitation_id": invitation_id }
		);
	}
}

class Client extends User {
	constructor(data) {
		super(data);
		this.friends 	= data.friends.map(friendData => new User(friendData));
		this.channels 	= data.channels.map(channelData => new Channel(channelData));
	}

	isFriend(user) {
		return this.friends.some(it => it.id === user.id);
	}

	addFriend(user) {
		return makeAPIRequest(
			"/api/user/client/friend/add",
			{ "user_id": user.id }
		);
	}

	removeFriend(user) {
		return makeAPIRequest(
			"/api/user/client/friend/remove",
			{ "user_id": user.id }
		);
	}

	static signup(first_name, last_name, username, password) {
		return makeAPIRequest(
			"/api/user/client/signup",
			{ 
				"first_name": first_name,
				"last_name": last_name,
				"username": username,
				"password": password
			}
		).then( response => new Client(JSON.parse(response)) );
	}

	static login(username, password) {
		return makeAPIRequest(
			"/api/user/client/login",
			{ 
				"username": username,
				"password": password
			}
		).then( response => new Client(JSON.parse(response)) );
	}

	static getClient() {
		return makeAPIRequest(
			"/api/user/client/get"
		).then(response => {
			if (response === null)
				return null;
			else
				return new Client(JSON.parse(response));
		});
	}

	static updateClientData(data) {
		return makeAPIRequest(
			"/api/user/client/update",
			{
				"first_name": this.first_name,
				"last_name": this.last_name,
				"description": this.description
			}
		);
	}
}

class Message {
	constructor(data) {
        this.id = data.id;
        this.text 		= data.text;
        this.datetime 	= Date.parse(data.datetime);
        this.channel 	= new Channel(data.channel);
        this.author 	= new User(data.author);
	}
}

// class MessagePage {
// 	constructor(data) {
// 		this.page 		= data.page;
// 		this.messages 	= data.messages;
// 	}	
// }

// class MessageList {
// 	_loading = false;

// 	isShouldLoadPreviousPage() {
// 		return !this._loading && this.pages[0].page !== 0;
// 	}

// 	async loadPreviousPage() {
// 		if (this.isShouldLoadPreviousPage()) {
// 			this._loading = true;

// 			let messagePageData = await makeAPIRequest(
// 				"/api/channel/load_messages", 
// 				{ 
// 					"channel_id": CHANNEL_ID, 
// 					"page": this.pages[0].page - 1
// 				}
// 			);
// 			let messageList = new MessageList(JSON.parse(messagePageData)["data"]);
// 			this.pages.splice(0, 0, ...messageList.pages);
			
// 			this._loading = false;

// 			return messageList;
// 		}
// 		else
// 			return null;
// 	}

// 	sendMessage(text) {
// 		let messageData = {
// 			"channel_id": this.channel.id,
// 			"text": text
// 		};
// 		return makeAPIRequest(
// 			"/api/channel/send_message",
// 			messageData
// 		).then(value => new Message(JSON.parse(value)["data"]));
// 	}

// 	constructor(data) {
// 		this.pages = [];
// 		for (let pageData of data.pages)
// 			this.pages.push(new MessagePage(pageData));
// 		this.channel = new Channel(data.channel);
// 	}

// 	static loadMessages() {
// 		let requestPromise = makeAPIRequest(
// 			"/api/channel/load_messages", 
// 			{ "channel_id": CHANNEL_ID }
// 		);

// 	    return requestPromise.then(value => {
// 			let data = JSON.parse(value)["data"];
// 			return new MessageList(data);
// 		});
// 	}
// }

function makeAPIRequest(url, data = {}) {
    return new Promise((resolve, reject) => {
        let xhr = new XMLHttpRequest();
        xhr.open("POST", url);
    	xhr.setRequestHeader("Content-Type", "application/json");
        
        xhr.onload = function () {
            if (this.status >= 200 && this.status < 300) {
                resolve(xhr.response);
            } else {
                reject({
                    status: this.status,
                    response: JSON.parse(this.response)
                });
            }
        };

        xhr.onerror = function () {
            reject({ status: this.status });
        };
        
        xhr.send(JSON.stringify(data));
    });
}
