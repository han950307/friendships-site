"use strict";

function displaySyncedMessages(json, firstLoad) {
    console.log(json);
	var first = parseInt($('#messages').attr('data-first'));
	if (firstLoad) {
	    first--;
	}
	$.each( json, function( key, value ) {
		if (value.pk > first) {
			$('#messages').append('<div>' + value.fields.content + '</div>');
			first = value.pk;
		}
	});

	$('#messages').attr('data-first', first);
}

function getMessages(repeat, firstLoad) {
	var dummy = $('#message_dummy');
    $.ajax({
        type: dummy.attr('data-method'),
        url: dummy.attr('data-action'),
        data: $('#message_form').serialize(),
		dataType: 'json',
		success: function (json) {
			displaySyncedMessages(json, firstLoad);
		}
    });
    if (repeat === true) {
    	setTimeout("getMessages(true, false)", 10000);
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
				getMessages(false, false);
            }
        });
        $('#form_message').val('');
    });

}

$(document).ready(function() {
	sendMessage();
	getMessages(true, true);
});