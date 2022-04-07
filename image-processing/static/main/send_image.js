const toBase64 = file => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
});

async function send_image(button) {
	let formData = new FormData(button.parentNode);
	let file  = formData.get("file");
	if (file) {
		let base64String = await toBase64(file);
		let response = await fetch("/api/image/add", {
			method: "POST",
			headers: {
		      "Content-Type": "application/json"
		    },
		    body: JSON.stringify({
		    	"image": base64String
		    })
		});
		// document.getElementById("response-text").innerText = response.json();
		console.log(await response.text());
	}
}