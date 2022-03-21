function update_profile(button) {
	let xhr = new XMLHttpRequest();
	xhr.open('POST', '/api/user/update_profile', true);
	xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

	xhr.onload = function () {
		if (this.status === 200) {
			let response = JSON.parse(this.response);
			alert(response["description"]);
		}
		else
			alert("Error with error code: " + this.status);
	};

	let data = {};
	Array.from(button.parentNode.childNodes)
			.filter( node => node.tagName && node.tagName.toLowerCase() === "input" && node.getAttribute("type") === "text" )
			.forEach( node => data[node.getAttribute("name")] = node.value )

	xhr.send(JSON.stringify(data));
}