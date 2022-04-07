var client;

( async () => client = await Client.getClient() )();

async function update_profile(button) {
	if (!client)
		return;
	let formData = new FormData(button.parentNode);

	client.first_name = formData.get("first_name");
	client.last_name = formData.get("last_name");
	client.description = formData.get("description");

	try {
		await client.update();
		pushMessagesList.addMessage(new PushMessage("Saved", "ok_message"));
	} catch (error) {
		if (error.status === 400 || error.status === 404)
			pushMessagesList.addMessage(new PushMessage("Something is wrong with your parameters", "error"));
		else 
			pushMessagesList.addMessage(new PushMessage("Error, try again later", "error"));
	}
}

async function use_invitation(invitation_id) {
	let newChannel = await ChannelInvitation.useInvitation(invitation_id);
	window.location = "/channels";
}

async function delete_invitation(invitation_id) {
	await ChannelInvitation.deleteInvitation(invitation_id);
	location.reload();
}