function resize(){
    var chart = $("#chart");
    $(chart).attr('height', 0.4 * $(window).height());
    $(chart).attr('width', $(chart).parent().outerWidth());
    console.log($(window).height());
}
$(document).ready(function(){
    resize();
    $(window).on("resize", function(){
        resize();
    });
});