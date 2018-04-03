"use strict";

var prev = null;

$('.sidebar-btn').click( function() {
    var id = $(this).attr("id");
    $('.message_dummy').hide();
    $('#messages-' + id).show();
    $(this).addClass('ui-gradient-purple');
    $('#' + prev).removeClass('ui-gradient-purple');
    $('#message_form').off("submit");
    sendMessage(id);
    prev = id;
});

function addSyncedMessages(json, firstLoad, id) {
	var first = parseInt($('#messages-' + id).attr('data-first'));
	$.each( json, function( key, value ) {
		if (value.pk > first && value.fields.transaction == id) {
			$('#messages-' + id).append('<div>' + value.fields.content + '</div>');
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
    alert('yooo');
    var first = true;
    var first_id = '';
    $('.message_dummy').each( function(index) {
        var id = $(this).attr("id").split("-")[1];
        if (first) {
            first = false;
            first_id = id;
        }
//        sendMessage(id);
	    getMessages(true, true, id);
    } );
    $('.message_dummy').hide();
    $('#messages-' + first_id).show();
    sendMessage(first_id);
    $('#' + first_id).addClass('ui-gradient-purple');
    prev = first_id;
});