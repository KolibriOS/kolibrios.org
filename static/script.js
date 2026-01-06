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
    }
}

function checkkey(e) {
    var keycode = window.event ? e.keyCode : e.which;
    if (keycode == 27) { dropdown_hide(); }
}
