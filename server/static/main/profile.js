var clientUser, currentUser;
var friendsNode;

function updateButton() {
	if (clientUser.isFriend(currentUser))
		setRemoveFromFriendsButton();
	else
		setAddToFriendButton();
}

socketio.on("user_private_data_changed", newClientData => {
	clientUser = new Client(newClientData);
	updateButton();
});

function clearFriendNode () {
	while (friendsNode.firstChild)
		friendsNode.removeChild(friendsNode.firstChild);
}

function setAddToFriendButton() {
	clearFriendNode();

	let button = document.createElement("input");
	button.type = "submit";
	button.value = "Add to friends";
	button.classList.add("base_input");
	button.classList.add("base_submit_input");
	button.onclick = async () => {
		await clientUser.addFriend(currentUser);
		updateButton();
	};

	friendsNode.appendChild(button);
}

function setRemoveFromFriendsButton() {
	clearFriendNode();

	let button = document.createElement("input");
	button.type = "submit";
	button.value = "Remove from friends";
	button.classList.add("base_input");
	button.classList.add("base_submit_input");
	button.onclick = async () => {
		await clientUser.removeFriend(currentUser);
		updateButton();
	};

	friendsNode.appendChild(button);
}

window.onload = async () => {
	clientUser = await Client.getClient();
	currentUser = await User.getUser(USER_ID);

	if (clientUser && clientUser.id !== currentUser.id) {
		friendsNode = document.getElementById("friend-relationship");
		updateButton();
	}
};
