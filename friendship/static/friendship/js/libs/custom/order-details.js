var order_steps = [
    'Item Requested',
    'Finding match',
    'Confirm price and Payment',
    'Item Ordered from Original Seller',
    'Sender received item',
    'Arrived in Thailand',
    'Delivered',
]

function addDivs() {
    for (var i = 0; i<order_steps.length; i++) {
        var step = order_steps[i];
        $('#actions').append('<div class="btn">' + step + '</div><br />');
    }
}


$(function() {
    addDivs();
});