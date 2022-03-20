function add_friend(user_id) {
	var xhr = new XMLHttpRequest();
	xhr.open('POST', '/api/user/add-friend', true);
	xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

	xhr.onload = function () {
		alert(this.status);
	};

	xhr.send(JSON.stringify({
		"user_id": user_id
	}));
}

function remove_friend(user_id) {
	var xhr = new XMLHttpRequest();
	xhr.open('POST', '/api/user/remove-friend', true);
	xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

	xhr.onload = function () {
		alert(this.status);
	};

	xhr.send(JSON.stringify({
		"user_id": user_id
	}));
}