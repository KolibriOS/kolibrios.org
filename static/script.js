function dropdown_show(el) {
    let x = 0;
    let y = 0;
    while (el) {
        x += el.offsetLeft;
        y += el.offsetTop;
        el = el.offsetParent;
    }
    const ddown = document.getElementById("lang-dropdown");
    ddown.style.display = "block";
    ddown.style.left = (x - 72) + "px";
    if (ddown.offsetLeft + ddown.offsetWidth + 10 > document.body.offsetWidth) {
        ddown.style.left = (document.body.offsetWidth - ddown.offsetWidth - 82) + "px";
    }
    ddown.style.top = (y + 48) + "px";
    fade_to(ddown, 1);
}

function dropdown_hide(e) {
    for (let t = e && e.target; t; t = t.parentElement) {
        if (t.id === "lang-dropdown" || t.id === "lang-butt") return;
    }
    const ddown = document.getElementById("lang-dropdown");
    fade_to(ddown, 0, function() {
        ddown.style.display = "none";
    });
}

function fade_to(el, target, done) {
    const from = parseFloat(el.style.opacity) || 0;
    const delta = target - from;
    let start;
    function step(ts) {
        if (!start) start = ts;
        const t = Math.min((ts - start) / 200, 1);
        el.style.opacity = from + delta * t;
        if (t < 1) requestAnimationFrame(step);
        else if (done) done();
    }
    requestAnimationFrame(step);
}

