/*  LANGUAGE DROPDOWN  */

function dropdown_show(obj)
{
    var x = y = 0;
    
    while(obj)
    {
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

    ddown.style.top = (y + 48) + "px";
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
    if(op < x)
    {
        op += 0.2;
        ddown.style.opacity = op;
        ddown.style.filter  = 'alpha(opacity=' + op * 100 + ')';
        t = setTimeout('appear(' + x + ')', 20);
    }
}

/*  SCREENSHOTS GALLERY  */

var FIRST_IMG_ID = 1;
var LAST_IMG_ID = 6;
var current = LAST_IMG_ID;  // start with last slide so that next() shows the first

window.onload = function() {
    // Dynamically create dots based on number of slides
    var dots = document.getElementById("dots");
    for (var i = FIRST_IMG_ID; i <= LAST_IMG_ID; i++) {
        var dot = document.createElement("span");
        dot.className = "dot" + (i === current ? " active" : "");
        dot.setAttribute("data-slide", i);
        dot.onclick = function() {
            goToSlide(parseInt(this.getAttribute("data-slide")));
        };
        dots.appendChild(dot);
    }
    // If a carousel element exists, advance to the first slide on load
    if (document.getElementById("carousel")) next();
};

function updateDots() {
    var dots = document.querySelectorAll("#dots .dot");
    dots.forEach(function(dot, index) {
        // index starts at 0 so add FIRST_IMG_ID to match your slide IDs
        dot.className = "dot" + ((index + FIRST_IMG_ID) === current ? " active" : "");
    });
}

function goToSlide(n) {
    if (n === current) return;
    document.getElementById("slide" + current).className = "minislide";
    current = n;
    document.getElementById("slide" + current).className = "visible";
    if (document.getElementById("carousel")) {
        document.getElementById("carousel").innerHTML = document.getElementById("slide" + current).alt;
    }
    updateDots();
}

function next() {
    document.getElementById("slide" + current).className = "minislide";
    if (current >= LAST_IMG_ID) {
        current = FIRST_IMG_ID;
    } else {
        current++;
    }
    document.getElementById("slide" + current).className = "visible";
    if (document.getElementById("carousel")) {
        document.getElementById("carousel").innerHTML = document.getElementById("slide" + current).alt;
    }
    updateDots();
}

function previous() {
    document.getElementById("slide" + current).className = "minislide";
    if (current <= FIRST_IMG_ID) {
        current = LAST_IMG_ID;
    } else {
        current--;
    }
    document.getElementById("slide" + current).className = "visible";
    if (document.getElementById("carousel")) {
        document.getElementById("carousel").innerHTML = document.getElementById("slide" + current).alt;
    }
    updateDots();
}

function checkkey(e) {
    var keycode = window.event ? e.keyCode : e.which;
    if (keycode == 37) { previous(); }
    else if (keycode == 39) { next(); }
    else if (keycode == 27) { dropdown_hide(); }
}
