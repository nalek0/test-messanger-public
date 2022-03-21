function add_friend(user_id) {
	let xhr = new XMLHttpRequest();
	xhr.open('POST', '/api/user/add_friend', true);
	xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

	xhr.onload = function () {
		if (this.status === 200) {
			let response = JSON.parse(this.response);
			alert(response["description"]);
		}
		else
			alert("Error with error code: " + this.status);
	};

	xhr.send(JSON.stringify({
		"user_id": user_id
	}));
}

function remove_friend(user_id) {
	let xhr = new XMLHttpRequest();
	xhr.open('POST', '/api/user/remove_friend', true);
	xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

	xhr.onload = function () {
		if (this.status === 200) {
			let response = JSON.parse(this.response);
			alert(response["description"]);
		}
		else
			alert("Error with error code: " + this.status);
	};

	xhr.send(JSON.stringify({
		"user_id": user_id
	}));
}