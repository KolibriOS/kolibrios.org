/* Screenshots galery */

var FIRST_IMG_ID = 1;
var LAST_IMG_ID = 6;
var current = LAST_IMG_ID;

window.onload = function() {
	if (document.getElementById("carousel")) next();
}

function checkkey(e)
{
	var keycode = window.event ? e.keyCode : e.which;
	if (keycode==37) { previous(); }
	else if (keycode==39) { next(); }
	else if (keycode==27) { dropdown_hide(); }
}

function next() {
	document.getElementById("slide"+current).className = "minislide";
	if (current >= LAST_IMG_ID) current = FIRST_IMG_ID; else current++;
	document.getElementById("slide"+current).className = "visible";
	document.getElementById("carousel").innerHTML = document.getElementById("slide"+current).alt;
}
function previous() {
	document.getElementById("slide"+current).className = "minislide";
	if (current <= FIRST_IMG_ID) current = LAST_IMG_ID; else current--;
	document.getElementById("slide"+current).className = "visible";
	document.getElementById("carousel").innerHTML = document.getElementById("slide"+current).alt;
}


/* DropDown */

function dropdown_show(obj)
{
	var x = y = 0;
	while(obj) {
		x += obj.offsetLeft;
		y += obj.offsetTop;
		obj = obj.offsetParent;
	}
	ddown = document.getElementById("lang-dropdown");
	ddown.style.display = "block";
	ddown.style.left    = (x - 64) + "px";
	if (ddown.offsetLeft + ddown.offsetWidth +10 > document.body.offsetWidth) 
	{
		ddown.style.left = document.body.offsetWidth - ddown.offsetWidth - 20 + "px";
	}
	ddown.style.top     = (y + 42) + "px";
	op = 0;
	appear(1);	
}

function dropdown_hide()
{
	ddown = document.getElementById("lang-dropdown");
	ddown.style.display="none";
}

function appear(x)
{
	if(op < x) {
		op += 0.2;
		ddown.style.opacity = op;
		ddown.style.filter='alpha(opacity='+op*100+')';
		t=setTimeout('appear('+x+')',20);
	}
}
