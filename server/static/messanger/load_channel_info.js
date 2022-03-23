window.onload = async () => {
	var client = await Client.getClient();
	var channel = await Channel.getChannel(CHANNEL_ID);

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
};