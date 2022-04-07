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

	update() {
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

	static createChannel(title, description, companions) {
		return makeAPIRequest(
			"/api/channel/create",
			{
				"title": title,
				"description": description,
				"companions": companions
			}
		).then ( response => new Channel(JSON.parse(response)) )
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

class MessagePage {
	constructor(data) {
		this.page 		= data.page;
		this.channel 	= new Channel(data.channel);
		this.messages 	= data.messages.map ( messageJson => new Message(messageJson) );
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

	static fetchMessages(channel_id, page=null, page_results=20) {
		let fetchData = {
			"channel_id": CHANNEL_ID, 
			"page_results": page_results
		}
		if (page != null)
			fetchData.page = page;

		return makeAPIRequest(
			"/api/channel/message/fetch", 
			fetchData
		).then( response => new MessagePage(JSON.parse(response)) );
	}

	static sendMessage(channel_id, text) {
		return makeAPIRequest(
			"/api/channel/message/send",
			{
				"channel_id": channel_id,
				"text": text
			}
		).then( response => new Message(JSON.parse(response)) );
	}
}

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
