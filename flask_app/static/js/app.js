$("#nav-trigger").click(function() {
    $("#sidebar").css("display", "block");
});

$("#nav-close").click(function() {
    $("#sidebar").css("display", "none");
});
$(".content").click(function() {
    $("#sidebar").css("display", "none");
});