$(function () {
    var picker = new Pikaday({
        field: document.getElementById('datepicker'),
        format: 'DD.MM.YYYY'
    });

    var startDatePicker = $('#start_date').pikaday({
        format: 'DD.MM.YYYY',
        firstDay: 1,
        minDate: new Date(2017, 10, 1),
        maxDate: new Date(),
        yearRange: [2017, 2018]
    });

    var endDatePicker = $('#end_date').pikaday({
        format: 'DD.MM.YYYY',
        firstDay: 1,
        minDate: new Date(2017, 10, 1),
        maxDate: new Date(),
        yearRange: [2017, 2018]
    });
});