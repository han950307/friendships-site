var order_steps = {
    0: 'Item Requested',
    1: 'Finding match',
    2: 'Confirm price and Payment',
    5: 'Item Ordered from Original Seller',
    6: 'Sender received item',
    7: 'Sender in transit',
    8: 'Arrived in Thailand',
    9: 'Delivered',
}

function addDivs() {
    var prev = -1;
    for (var key in order_steps){
        if ($("#" + key).length != 0) {
            $('#actions').append('<div class="btn ui-gradient-blue" id="btn-' + key + '">' +
                                 order_steps[key] + ': ' + $("#" + key).attr('data-date') + '</div><br />');
            prev = key;
        } else {
            $('#actions').append('<div class="btn ui-gradient-peach">' + order_steps[key] + '</div><br />');
        }
    }
    console.log($('#btn-' + prev).attr("class"));
    $('#btn-' + prev).removeClass('ui-gradient-blue').addClass('ui-gradient-green');
}


$(function() {
    addDivs();
});