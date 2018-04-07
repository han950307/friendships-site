"use strict";

var prev = null;

$('.sidebar-btn').click( function() {
    var id = $(this).attr("id");
    if (prev === id) {
        return;
    }
    $('.message_dummy').hide();
    var msg = $('#messages-' + id);
    msg.show();
    $(this).addClass('ui-gradient-message-selected');
    $(this).removeClass('ui-gradient-messages');
    $('#' + prev).removeClass('ui-gradient-message-selected');
    $('#' + prev).addClass('ui-gradient-messages');
    $('#message_form').off("submit");
    sendMessage(id);
    prev = id;
    // this doesn't work to scroll unfortunately
    msg.animate({scrollTop: msg.height()}, 'slow')
});

function addSyncedMessages(json, firstLoad, id) {
	var first = parseInt($('#messages-' + id).attr('data-first'));
	$.each( json, function( key, value ) {
		if (value.pk > first && value.fields.transaction == id) {

			$('#messages-' + id).append(
			'<p>' + value.fields.content + '</p>');
			first = value.pk;
		}
	});
	$('#messages-' + id).attr('data-first', first);
}

function getMessages(repeat, firstLoad, id) {
	var dummy = $('#messages-' + id);
    $.ajax({
        type: dummy.attr('data-method'),
        url: dummy.attr('data-sync'),
        data: $('#message_form').serialize(),
		dataType: 'json',
		success: function (json) {
			addSyncedMessages(json, firstLoad, id);
		}
    });
    if (repeat === true) {
    	setTimeout("getMessages(true, false," + id + ")", 10000);
    }
}

function sendMessage(id) {
	var frm = $('#message_form');
    frm.submit(function(e) {
    	e.preventDefault();
        $.ajax({
            type: $('#messages-' + id).attr('data-method'),
            url: $('#messages-' + id).attr('data-send'),
            data: frm.serialize(),
            success: function(response) {
				getMessages(false, false, id);
            }
        });
        $('#form_message').val('');
    });
}

$(document).ready(function() {
    var first = true;
    var first_id = '';
    $('.message_dummy').each( function(index) {
        var id = $(this).attr("id").split("-")[1];
        if (first) {
            first = false;
            first_id = id;
        }
	    getMessages(true, true, id);
    } );
    $('.message_dummy').hide();
    $('#messages-' + first_id).show();
    sendMessage(first_id);
    $('#' + first_id).removeClass('ui-gradient-messages');
    $('#' + first_id).addClass('ui-gradient-message-selected');
    prev = first_id;
});