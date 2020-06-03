/* Screenshots galery */

var FIRST_IMG_ID = 1;
var LAST_IMG_ID = 6;
var current = FIRST_IMG_ID;
var previews_visible = true;

function checkkey(e)
{
	var keycode = window.event ? e.keyCode : e.which;
	if (keycode==37) { previous(); }
	else if (keycode==39) { next(); }
	else if (keycode==27) { dropdown_hide(); }
}

window.onload = function() {
	if (document.getElementById("show"))
	if (document.getElementById("screen").offsetHeight <  1200) setTimeout( 'toggle_previews();', 1000);
}

function next() {
	document.getElementById("mslide"+current).className = "minislide";
	document.getElementById("slide"+current).className = "minislide";
	if (current >= LAST_IMG_ID) current = FIRST_IMG_ID; else current++;
	document.getElementById("slide"+current).className = "visible";
	document.getElementById("mslide"+current).className = "minislide active";
	document.getElementById("spoiler").innerHTML = document.getElementById("slide"+current).alt;
}
function previous() {
	document.getElementById("mslide"+current).className = "minislide";
	document.getElementById("slide"+current).className = "minislide";
	if (current <= FIRST_IMG_ID) current = LAST_IMG_ID; else current--;
	document.getElementById("slide"+current).className = "visible";
	document.getElementById("mslide"+current).className = "minislide active";
	document.getElementById("spoiler").innerHTML = document.getElementById("slide"+current).alt;
}
function mini(new_current) {
	document.getElementById("mslide"+current).className = "minislide";
	document.getElementById("slide"+current).className = "minislide";
	document.getElementById("slide"+new_current).className = "visible";
	document.getElementById("mslide"+new_current).className = "minislide active";
	document.getElementById("spoiler").innerHTML = document.getElementById("slide"+new_current).alt;
	current = new_current;
}

function toggle_previews() {
	if (previews_visible==true)
	{
		previews_visible=false;
		hide_previews(0);
	}
	else
	{
		previews_visible = true;
		document.getElementById("panel_minislides").style.height = "auto";
		document.getElementById("spoiler").style.borderBottom = "1px #555 solid";
	}
}

function hide_previews(i) {
	if (i<80) {
		document.getElementById("panel_minislides").style.height = 80 - i + "px";
		i+=3;
		setTimeout( 'hide_previews('+i+')', 1);
	}
	else
	{
		document.getElementById("spoiler").style.borderBottom = "0";
	}
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
	ddown.style.left    = (x - 72) + "px";
	if (ddown.offsetLeft + ddown.offsetWidth +10 > document.body.offsetWidth) 
	{
		ddown.style.left = document.body.offsetWidth - ddown.offsetWidth - 82 + "px";
	}
	ddown.style.top     = (y + 48) + "px";
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
