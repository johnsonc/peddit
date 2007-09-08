debug = true
function mod_link(linkid, direction){
	
	if (direction == 1)
	{
	   YAHOO.util.Connect.asyncRequest('GET', '/upvote/'+linkid, upvote_callback, null);
	   
	}
	else {
	   YAHOO.util.Connect.asyncRequest('GET', '/downvote/'+linkid, downvote_callback, null);
	}  
}

function save_link(linkid){
	   YAHOO.util.Connect.asyncRequest('GET', '/save/'+linkid, save_callback, null);
}

function upvoted(o){
	if (o.responseText == -1)
	{
		return
	}
	id = 'uplink'+ o.responseText+'img'
    elem = document.getElementById(id);
	elem.setAttribute('src', '/foo/upped.png');
	id = 'downlink'+ o.responseText+'img'
    elem = document.getElementById(id);
	elem.setAttribute('src', '/foo/down.png');
}

function downvoted(o){
	if (o.responseText == -1)
	{
		return
	}
	id = 'downlink'+ o.responseText+'img'
    elem = document.getElementById(id);
	elem.setAttribute('src', '/foo/downed.png');
	id = 'uplink'+ o.responseText+'img'
    elem = document.getElementById(id);
	elem.setAttribute('src', '/foo/up.png');
}
function saved(o){
	if (o.responseText == -1)
	{
		return
	}
	id = 'save'+ o.responseText
    elem = document.getElementById(id);
	elem.innerHTML = 'saved';	
}

function show_trace(o){
alert('Unexpected error')
document.write(o.responseText)
}


var upvote_callback =
{
	success: upvoted,
	failure: show_trace
}

var downvote_callback =
{
	success: downvoted,
	failure: show_trace
}
var save_callback =
{
    success: saved,
	failure: show_trace
}
