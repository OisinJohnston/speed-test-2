

document.addEventListener("DOMContentLoaded", () => {
	let restable = document.getElementById("singleresults");
	fetch(url = "./api/singleentries", {
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
	let twotable = document.getElementById("tworesults");
	fetch(url = "./api/twoentries", {method:"GET"}).then(async function(response) {
		var resp = await response.json();
		console.log(resp)
		for (var i = 0; i<resp.length; i++) {
			var item = resp[i]
			var row = twotable.insertRow(-1);
			row.insertCell(0).innerHTML = i+1;
			row.insertCell(1).innerHTML = item["player 1"]
			row.insertCell(2).innerHTML = item["player 2"]
			row.insertCell(3).innerHTML = item["winner"]
			row.insertCell(4).innerHTML = item["winnerscr"]
			row.insertCell(5).innerHTML = 5 - item["winnerscr"]
		}
	})

})



