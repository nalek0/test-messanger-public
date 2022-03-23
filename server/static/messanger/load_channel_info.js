var client;
var channel;

async function update_channel(button) {
	let data = {}
	Array.from(button.parentNode.childNodes)
			.filter( node => {
				return node.tagName && (
					(
						node.tagName.toLowerCase() === "input" && 
						(node.getAttribute("type") === "text" || node.getAttribute("type") === "hidden")
					) || node.tagName.toLowerCase() === "textarea"
				);
			})
			.forEach( node => data[node.getAttribute("name")] = node.value )
	try {
		await channel.updateChannelData(data);
		console.log("HERE");
		console.log(pushMessagesList);
		pushMessagesList.addMessage(new PushMessage("Saved", "ok_message"));
	} catch (error) {
		if (error.status === 400 || error.status === 404)
			pushMessagesList.addMessage(new PushMessage("Something is wrong with your parameters", "error"));
		else 
			pushMessagesList.addMessage(new PushMessage("Error, try again later", "error"));
	}
}

window.addEventListener("load", async () => {
	client = await Client.getClient();
	channel = await Channel.getChannel(CHANNEL_ID);

	// Chnanel info block:
	if (channel.getUserPermission(client).hasPermission(WATCH_CHANNEL_INFO)) {
		document.getElementById("channel_info_block").classList.remove("hidden");

		let adminsListNode = document.getElementById("admins_list");
		channel.getAdmins()
			.map( user => user.getLinkNode() )
			.forEach(node => {
				let liWrapper = document.createElement("li");
				liWrapper.appendChild(node);
				adminsListNode.appendChild(liWrapper);
			});

		let moderatorsListNode = document.getElementById("moderators_list");
		channel.getModerators()
			.map( user => user.getLinkNode() )
			.forEach(node => {
				let liWrapper = document.createElement("li");
				liWrapper.appendChild(node);
				moderatorsListNode.appendChild(liWrapper);
			});


		let membersListNode = document.getElementById("members_list");
		channel.getMembers()
			.map( user => user.getLinkNode() )
			.forEach(node => {
				let liWrapper = document.createElement("li");
				liWrapper.appendChild(node);
				membersListNode.appendChild(liWrapper);
			});
	}
	if (channel.getUserPermission(client).hasPermission(EDIT_CHANNEL)) {
		document.getElementById("moderator_block").classList.remove("hidden");
	}
});