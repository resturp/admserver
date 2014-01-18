var timeout = null;

function initPage() {
	showTask('task1');
    
	mainElem = document.getElementById("tableAssignment");
	hideDetail(mainElem.rows[1],0);
	mainElem.onmouseover = function() {showDetail(mainElem.rows[1],400);};
	mainElem.onmouseout = function() {hideDetail(mainElem.rows[1],200);};	
}

function showDetail(elem, ms) {
	clearTimeout(timeout);
	timeout = setTimeout(function() {elem.style.display = '';}, ms);
}

function hideDetail(elem, ms) {
	clearTimeout(timeout);
	timeout = setTimeout(function() {elem.style.display = 'none';}, ms);
}

function showTask(taskName) {
    var table = document.getElementById("myTable");
	$(":input").attr('disabled', false);
	for (var i = 0, row; row = table.rows[i]; i++) {
        if (row.id.substring(0,4) == "task") {
        	
            if (row.id == taskName) {
            	row.style.display = '';
                document.getElementById("task"+i).style.color = "#000";
                document.getElementById("task"+i).style.background = "#efefef";
                
                if (document.getElementById("task"+i+"attempts").value != 'inf'){
                	if (parseInt(document.getElementById("task"+i+"attempts").value) < 1) {
                		$(":input").attr('disabled', true);
                	}
                } 
                
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
		
		if (http.status == 200) {
			switch(http.readyState) {
			case 3:
				document.getElementById("Response" + task).innerHTML = "Processing .....\n\n" + http.responseText;
				break;
			case 4:
				document.getElementById("Response" + task).innerHTML = "Done .....\n\n" + http.responseText;
			}
		} 
	}

	http.send(params);
	

	
    if (document.getElementById("task" + task + "attempts").value != 'inf'){
    	newval = parseInt(document.getElementById("task" + task + "attempts").value) - 1;
    	document.getElementById("attempts" + task).innerHTML = newval;
    	document.getElementById("task" + task + "attempts").value = newval;
    	showTask("task" + task);
    }
    

	
}



