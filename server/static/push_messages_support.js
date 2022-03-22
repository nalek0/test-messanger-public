let url = new URL(window.location.href);

let errors = url.searchParams.getAll("errors");
if (errors){
	for (let error of errors)
		pushMessagesList.addMessage(new PushMessage(error, "error"));
}
