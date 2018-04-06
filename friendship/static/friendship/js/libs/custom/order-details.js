

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
    alert(info);
    addDivs();
});

//timer


  var datetime = document.getElementById('order-bid-end-time').getAttribute('datetime');
  var deadline = new Date(datetime).getTime();

  setInterval(function() {
    var now = new Date().getTime();
    var distance = deadline-now;
    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((distance % (1000 * 60)) / 1000);

  	document.getElementById('time_countdown').innerHTML = hours+":"+minutes+":"+seconds;
  	}, 1000);



//payment radio button listeners
  var creditCardRadio = document.getElementById('credit-card-radio');
  var wireRadio = document.getElementById('wire-radio');
  creditCardRadio.onclick= function(){
    document.getElementById('credit-card-payment').style.display = "block";
    document.getElementById('wire-payment').style.display = "none";
  }
  wireRadio.onclick= function(){
    document.getElementById('credit-card-payment').style.display = "none";
    document.getElementById('wire-payment').style.display = "block";
  }
