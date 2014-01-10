function showTask(taskName) {
    var table = document.getElementById("myTable");
    for (var i = 0, row; row = table.rows[i]; i++) {
        if (row.id.substring(0,4) == "task") {
            if (row.id == taskName) {
            	row.style.display = '';
                document.getElementById("task"+i).style.color = "#000";
                document.getElementById("task"+i).style.background = "#efefef";
            } else {
            	row.style.display = 'none';
                document.getElementById("task"+i).style.color = "#fff";           
            	document.getElementById("task"+i).style.background = "#000";
            }
        }
    }

}

function processSubmission(task) {
	var http = new XMLHttpRequest();
	var url = "/assignment";
	var params = "";
	
	$("#task" + task + " input").each( function() {
		params += this.name + "=" + encodeURIComponent(this.value) + "&"
	})
	$("#task" + task + " textarea").each( function() {
		params += this.name + "=" + encodeURIComponent(this.value)
	})
	
	document.getElementById("Response" + task).innerHTML = "Processing .....\n\n";
	
	http.open("POST", url, true);

	//alert(params);

	//Send the proper header information along with the request
	http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	http.setRequestHeader("Content-length", params.length);
	http.setRequestHeader("Connection", "close");

	
	http.onreadystatechange = function () {
		
		if(http.readyState == 3 && http.status == 200) {
			document.getElementById("Response" + task).innerHTML = "Processing .....\n\n" + http.responseText;
		}
		
		if(http.readyState == 4 && http.status == 200) {
			document.getElementById("Response" + task).innerHTML = "Done .....\n\n" + http.responseText;
		}

	}

	http.send(params);


}



