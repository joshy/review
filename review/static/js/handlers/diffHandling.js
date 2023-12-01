$(function () {
    if ('diff' === $('body').data('page')) {
        diff();
    }

    function diff() {
        var writing = $('#writing').text();
        var final = $('#final').text();
        var diff = JsDiff.diffWords(writing, final);
        var display = $('#diff').get(0);
        while (display.firstChild) {
            display.removeChild(display.firstChild);
        }
        var fragment = document.createDocumentFragment();

        diff.forEach(function (part) {
            // green for additions, red for deletions
            // grey for common parts
            color = part.added ? 'green' :
                part.removed ? 'red' : 'grey';
            span = document.createElement('span');
            span.style.color = color;
            if (part.removed === true) {
                span.className = "strike";
            }
            span.appendChild(document.createTextNode(part.value));
            fragment.appendChild(span);
        });
        display.appendChild(fragment);
    }

    $('input[type=radio][name=report_text]').on('change', function () {
        // gets the value from the hidden elements #report_s or # report_v 
        var x = document.getElementById(this.value).innerHTML;
        // and sets that to the first div
        $('#writing').html(x);
        diff();
        if (this.value === 'report_s') {
            $('#hedging_score_v').addClass('dn');
            $('#hedging_score_s').removeClass('dn');
            $('#words_added_v_f').addClass('dn');
            $('#words_deleted_v_f').addClass('dn');
            $('#jaccard_v_f').addClass('dn');
            $('#words_added_s_f').removeClass('dn');
            $('#words_deleted_s_f').removeClass('dn');
            $('#jaccard_s_f').removeClass('dn')
        } else if (this.value === 'report_v') {
            $('#hedging_score_s').addClass('dn');
            $('#hedging_score_v').removeClass('dn');
            $('#words_added_v_f').removeClass('dn');
            $('#words_deleted_v_f').removeClass('dn');
            $('#jaccard_v_f').removeClass('dn');
            $('#words_added_s_f').addClass('dn');
            $('#words_deleted_s_f').addClass('dn');
            $('#jaccard_s_f').addClass('dn')
        }
    });
});