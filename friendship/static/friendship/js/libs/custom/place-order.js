function addForm() {
    var form_idx = parseInt($('#id_form-TOTAL_FORMS').val());
    $('#id_form-TOTAL_FORMS').val(form_idx + 1);

    $('#all_forms').append('<div class="container info-container rounded" id="container-' + form_idx +  '">');


    $('#container-' + form_idx).append('<div class="container" id="info-' + form_idx +  '">' +
                                       '<div class="row align-items-center"><h3 id="header-' + form_idx + '">Item</h3>' +
                                       '<i class="toggler fa fa-chevron-up" id="toggle-' + form_idx + '"></i>' +
                                       '<i class="remover fa fa-times-circle" id="remove-' + form_idx + '"></i>');

    $('#container-' + form_idx).append('<div id="form-' + form_idx + '">');
    $('#form-' + form_idx).append($('#empty_form').html().replace(/__prefix__/g, form_idx));
    $('#form-' + form_idx).append('<br />');
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

// this is hacky and I don't like it at ALL but yolo MVP
function customizeForm() {
    var type = $('#id_form-__prefix__-merchandise_type');
    var quantity = $('#id_form-__prefix__-quantity');
    $('#id_form-__prefix__-url').after('<div class="container"><div class="row" id="id_form-__prefix__-row">');
    $('#id_form-__prefix__-row').append('<div class="col" id="id_form-__prefix__-type-container">');
    $('#id_form-__prefix__-type-container').append(type);
    $('#id_form-__prefix__-row').append('<div class="col" id="id_form-__prefix__-quantity-container">');
    $('#id_form-__prefix__-quantity-container').append(quantity);
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

$(function() {
    var form_idx = parseInt($('#id_form-TOTAL_FORMS').val()) - 1;
    $('#id_form-TOTAL_FORMS').val(form_idx);
    customizeForm();
    addForm();
});

