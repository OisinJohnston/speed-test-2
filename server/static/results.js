

document.addEventListener("DOMContentLoaded", () => {
	let restable = document.getElementById("results");
	fetch(url = "/api/entries", {
		method: 'GET'
	}).then(async function(response) {
		var resp = await response.json();
		console.log(resp)
		for (var i = 0; i<resp.length; i ++) {
			var item = resp[i]
			var row = restable.insertRow(-1);
			var poscell = row.insertCell(0);
			var namecell = row.insertCell(1);
			var timecell = row.insertCell(2);

            poscell.innerHTML  = i + 1
            namecell.innerHTML = item["user"]["name"];
			timecell.innerHTML = item["timetaken"];

        }
    })
})



