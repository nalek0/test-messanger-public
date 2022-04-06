async function login(button) {
	let formData = new FormData(button.parentNode);
	try {
		let client = await Client.login(
			formData.get("username"), 
			formData.get("password")
		);
		window.location.href = client.profile_url;
	} catch (error) {
		if (error.status && error.response)
			pushMessagesList.addMessage(new PushMessage(error.response.description, "error"));
		else
			pushMessagesList.addMessage(new PushMessage("Error with the internet connection", "error"));
	}
}