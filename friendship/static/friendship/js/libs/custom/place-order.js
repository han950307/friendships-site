"use strict";

function addForm() {
    var form_idx = parseInt($('#id_form-TOTAL_FORMS').val());
    $('#id_form-TOTAL_FORMS').val(form_idx + 1);
    $('#all_forms').append($('#empty_form').html().replace(/__prefix__/g, form_idx));
}

function toggle(id) {
    var url = $('#id_form-' + parseInt(id) + '-url').val();
    if($('#form-' + id).css('display') === 'none') {
        $("#header-" + id).replaceWith('<h3 id="header-' + id + '">Item</h3>');
        $('#form-' + id).show("fast");
        $("#toggle-" + id).removeClass("fa-chevron-down").addClass("fa-chevron-up");
    } else {
        $("#header-" + id).replaceWith('<h6 id="header-' + id + '">Item</h6>');
        $('#form-' + id).hide("fast");
        $("#toggle-" + id).removeClass("fa-chevron-up").addClass("fa-chevron-down");
    }
    if (url !== '') {
        $('#header-' + id).text(url);
    }

}

function remove(id) {
    var form_idx = parseInt($('#id_form-TOTAL_FORMS').val()) - 1;
    $('#id_form-TOTAL_FORMS').val(form_idx);
    $('#container-' + id).remove();
    var prefixes = ['info', 'header', 'toggle', 'remove', 'form', 'container']
    for (var i = id; i<form_idx; i++) {
        for (var k = 0; k<prefixes.length; k++) {
            console.log('#' + prefixes[k] + '-' + (parseInt(i)+1));
            console.log($('#' + prefixes[k] + '-' + (parseInt(i)+1)));
            $('#' + prefixes[k] + '-' + (parseInt(i)+1)).attr('id', prefixes[k] + '-' + i);
        }
    }
}

function customizeForm() {
    var type = $('#id_form-__prefix__-merchandise_type');
    type.attr("style", "height:35px;");
}

$('#add_more').click(function() {
    addForm();
});

$(document).on("click", ".toggler", function(e){
    var id = this.id.split("-")[1];
    toggle(id);
});

$(document).on("click", ".remover", function(e){
    var id = this.id.split("-")[1];
    remove(id);
});


$(document).on("click", ".remover", function(e){
    var id = this.id.split("-")[1];
    remove(id);
});


$(function() {
    var form_idx = parseInt($('#id_form-TOTAL_FORMS').val()) - 1;
    $('#id_form-TOTAL_FORMS').val(form_idx);
    customizeForm();
    addForm();
});

