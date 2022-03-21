function send_message() {
	let textarea = document.getElementById("message_textarea");
	let text = textarea.value;
	textarea.value = "";

	let xhr = new XMLHttpRequest();
	xhr.open('POST', '/api/channel/send_message', true);
	xhr.setRequestHeader("Content-Type", "application/json; charset=utf-8");

	xhr.onload = function () {
		if (this.status === 200) {
			let response = JSON.parse(this.response);
			console.log(response["description"]);
		}
		else
			console.log("Error with error code: " + this.status);
	};

	xhr.send(JSON.stringify({
		"channel_id": CHANNEL_ID,
		"text": text
	}));
}

window.onload = () => {
	let xhr = new XMLHttpRequest();
	xhr.open('POST', '/api/channel/load_messages', true);
	xhr.setRequestHeader("Content-Type", "application/json; charset=utf-8");

	xhr.onload = function () {
		if (this.status === 200) {
			let response = JSON.parse(this.response);
			console.log(response["data"]);
		}
		else
			console.log("Error with error code: " + this.status);
	};

	xhr.send(JSON.stringify({
		"channel_id": CHANNEL_ID
	}));
};