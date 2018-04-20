var order = document.getElementsByClassName('order-bid-end-time');
var orders = [];
for(var i=0; i<order.length; i++){
  orders.push([order[i].getAttribute('title'),order[i].getAttribute('datetime')]);
}

//update timer countdown per second
setInterval(function() {
  var now = new Date().getTime();
  for(var i=0; i<orders.length; i++){
    var id = orders[i][0];
    var deadline = new Date(orders[i][1]).getTime();
    var distance = deadline-now;
    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((distance % (1000 * 60)) / 1000);
    document.getElementById(id).innerHTML = twoDigit(hours)+":"+twoDigit(minutes)+":"+twoDigit(seconds);
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
