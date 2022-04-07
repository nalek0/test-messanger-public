async function create_channel(button) {
	let formData = new FormData(button.parentNode);
	try {
		let channel = await Channel.createChannel(
			formData.get("title"), 
			formData.get("description"), 
			formData.get("companions")
		);
		window.location.href = `/messanger/channel/${channel.id}`;
	} catch (error) {
		if (error.status && error.response)
			pushMessagesList.addMessage(new PushMessage(error.response.description, "error"));
		else
			pushMessagesList.addMessage(new PushMessage("Error with the internet connection", "error"));
	}
}