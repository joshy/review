//Delete local Storage every time Dashboard reentered
$(".dashboardRow").on('click', function () {
    localStorage.clear();
});