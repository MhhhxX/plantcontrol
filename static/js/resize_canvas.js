function resize(){
    var chart = $("#chart");
    var chartContainer = $(chart).parent();
    var windowHeight = Math.floor($(window).height());

    // set min-width to 50 * dataPrecision
    $(chart).css("min-width", "1250px");

    // mobile browsers calculate dimension values differently
    if ($(window).width() < 768) {
        $(chartContainer).css('height', 0.15 * windowHeight + "px");
    }
    else
        $(chartContainer).css('height', 0.25 * windowHeight + "px");
}
