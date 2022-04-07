var client;
var channel;

async function update_channel(button) {
	let formData = new FormData(button.parentNode);
	channel.title = formData.get("title");
	channel.description = formData.get("description");

	try {
		await channel.update();
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
	client_member = await channel.getMember(client);

	// Chnanel info block:
	if (client_member.hasPermission("watch_channel_information_permission")) {
		document.getElementById("channel_info_block").classList.remove("hidden");

		let moderatorsListNode = document.getElementById("moderators_list");
		(await channel.getModerators())
			.map( channel_member => channel_member.user.getLinkNode() )
			.forEach(node => {
				let liWrapper = document.createElement("li");
				liWrapper.appendChild(node);
				moderatorsListNode.appendChild(liWrapper);
			});
			


		let membersListNode = document.getElementById("members_list");
		(await channel.getMembers())
			.map( channel_member => channel_member.user.getLinkNode() )
			.forEach(node => {
				let liWrapper = document.createElement("li");
				liWrapper.appendChild(node);
				membersListNode.appendChild(liWrapper);
			});
	}
	if (client_member.hasPermission("edit_channel_permission")) {
		document.getElementById("moderator_block").classList.remove("hidden");
	}
});