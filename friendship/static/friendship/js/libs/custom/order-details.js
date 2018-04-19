  var datetime = document.getElementById('order-bid-end-time').getAttribute('datetime');
  var deadline = new Date(datetime).getTime();
  var paymentDeadline = new Date(datetime);
  paymentDeadline.setDate(paymentDeadline.getDate() + 1);
  var paymentDeadlineTime = paymentDeadline.getTime();

  setInterval(function() {
    var now = new Date().getTime();
    var distance = deadline-now;
    var distance2 = paymentDeadlineTime - now;
    if (distance > 0){
      var hours = Math.floor(distance/ (1000 * 60 * 60));
      var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      var seconds = Math.floor((distance % (1000 * 60)) / 1000);
    	document.getElementById('time_countdown').innerHTML = "<h5>"+twoDigit(hours)+":"+twoDigit(minutes)+":"+twoDigit(seconds)+"</h5>";

    } else if (distance2 > 0) {
      var hours2 = Math.floor(distance2/ (1000 * 60 * 60));
      var minutes2 = Math.floor((distance2 % (1000 * 60 * 60)) / (1000 * 60));
      var seconds2 = Math.floor((distance2 % (1000 * 60)) / 1000);
      var displayTime = twoDigit(hours2)+":"+twoDigit(minutes2)+":"+twoDigit(seconds2);
      document.getElementById('payment-timer').innerHTML = "<div style='font-family: ThaiLight'>Please confirm price and pay within "+ displayTime + " or your order will automatically be cancelled.</div>";
    
    } else {
      document.getElementById('time_countdown').innerHTML = "<h5>finding match now...</h5>";
    }
  }, 1000);

//convert the time to 2 digits (ex. 5 -> 05)
function twoDigit(num) {
  var n = num.toString();
  if(n.length == 1){
    return "0"+n;
  }
  return n;
}

//payment radio button listeners
  var creditCardRadio = document.getElementById('credit-card-radio');
  var wireRadio = document.getElementById('wire-radio');
  var onlineWireRadio = document.getElementById('bank-transfer-online-radio');
  creditCardRadio.onclick= function(){
    document.getElementById('credit-card-payment').style.display = "block";
    document.getElementById('wire-payment').style.display = "none";
    document.getElementById('online-wire-transfer').style.display = "none";
  }
  wireRadio.onclick= function(){
    document.getElementById('credit-card-payment').style.display = "none";
    document.getElementById('wire-payment').style.display = "block";
    document.getElementById('online-wire-transfer').style.display = "none";
  }
  onlineWireRadio.onclick= function(){
    document.getElementById('credit-card-payment').style.display = "none";
    document.getElementById('wire-payment').style.display = "none";
    document.getElementById('online-wire-transfer').style.display = "block";
  }

// function on() {
//     document.getElementById("overlay").style.display = "block";
// }

// function off() {
//     document.getElementById("overlay").style.display = "none";
// }

// $( document ).ready(function() {
//     on();
// });
