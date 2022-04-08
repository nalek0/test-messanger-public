var client;

( async () => client = await Client.getClient() )();

function toBase64(file) {
	return new Promise((resolve, reject) => {
	    const reader = new FileReader();
	    reader.readAsDataURL(file);
	    reader.onload = () => resolve(reader.result);
	    reader.onerror = error => reject(error);
	});
}

async function update_profile(button) {
	if (!client)
		return;
	let formData = new FormData(button.parentNode);

	client.first_name = formData.get("first_name");
	client.last_name = formData.get("last_name");
	client.description = formData.get("description");

	// try {
		await client.update();

		let file = formData.get("avatar");
		if (file.size > 0) {
			let base64String = await toBase64(file);
			await client.updateAvatar(base64String);
		}

		console.log(client);

		pushMessagesList.addMessage(new PushMessage("Saved", "ok_message"));
	// } catch (error) {
	// 	if (error.status === 400 || error.status === 404)
	// 		pushMessagesList.addMessage(new PushMessage("Something is wrong with your parameters", "error"));
	// 	else 
	// 		pushMessagesList.addMessage(new PushMessage("Error, try again later", "error"));
	// }
}

async function use_invitation(invitation_id) {
	let newChannel = await ChannelInvitation.useInvitation(invitation_id);
	window.location = "/channels";
}

async function delete_invitation(invitation_id) {
	await ChannelInvitation.deleteInvitation(invitation_id);
	location.reload();
}