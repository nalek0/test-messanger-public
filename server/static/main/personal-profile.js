async function update_profile(button) {
	let data = {}
	Array.from(button.parentNode.childNodes)
			.filter( node => node.tagName && ((node.tagName.toLowerCase() === "input" && node.getAttribute("type") === "text") || node.tagName.toLowerCase() === "textarea")  )
			.forEach( node => data[node.getAttribute("name")] = node.value )
	try {
		await Client.updateClientData(data);
		pushMessagesList.addMessage(new PushMessage("Saved", "ok_message"));
	} catch (error) {
		if (error.status === 400 || error.status === 404)
			pushMessagesList.addMessage(new PushMessage("Something is wrong with your parameters", "error"));
		else 
			pushMessagesList.addMessage(new PushMessage("Error, try again later", "error"));
	}
}

async function delete_invitation(invitation_id) {
	await ChannelInvitation.deleteInvitation(invitation_id);
	location.reload();
}