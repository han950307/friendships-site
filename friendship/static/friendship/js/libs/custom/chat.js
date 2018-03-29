function displaySyncedMessages(json) {
//    alert(JSON.stringify(json));
	var first = $('#messages').attr('data-first');
//	alert(first);
	$.each( json, function( key, value ) {
		if (value.pk > first) {
			$('#messages').append('<div>' + value.fields.content + '</div>');
			first = value.pk;
		}
//		alert(first);
	});

	$('#messages').attr('data-first', first);
}

function getMessages(repeat) {
	var dummy = $('#message_dummy');
    $.ajax({
        type: dummy.attr('data-method'),
        url: dummy.attr('data-action'),
        data: $('#message_form').serialize(),
		dataType: 'json',
		success: function (json) {
			displaySyncedMessages(json);
		}
    });
    if (repeat === true) {
    	setTimeout("getMessages(true)", 10000);
    }
}

function sendMessage() {
	var frm = $('#message_form');
    frm.submit(function(e) {
    	e.preventDefault();
        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: frm.serialize(),
            success: function(response) {
				getMessages(false);
            }
        });
        $('#form_message').val('');
    });

}



$(document).ready(function() {
	sendMessage();
	getMessages(true);
});