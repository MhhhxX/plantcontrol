var mql = window.matchMedia("(orientation: portrait)").matches;

function resize(){
    var chart = $("#chart");
    var chartContainer = $(chart).parent();
    var windowHeight = Math.floor($(window).height());

    if ($(window).width() <= 767.98)
        $(chartContainer).css('height', 0.15 * windowHeight + "px");
    else
        $(chartContainer).css('height', 0.25 * windowHeight + "px");
}

$(document).ready(function(){
    resize();

        $(window).on("resize", function () {
            if ($(window).width() <= 767.98) {
                var newMql = window.matchMedia("(orientation: portrait)").matches;
                if (mql && !newMql) {
                    mql = newMql;
                    resize();
                } else if (!mql && newMql) {
                    mql = newMql;
                    resize();
                }
            } else {
                resize();
            }
        });

});
