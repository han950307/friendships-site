$('#add_more').click(function() {
    var form_idx = parseInt($('#id_form-TOTAL_FORMS').val()) + 1;
    var formNum = 'form-' + form_idx;
    $('#all_forms').append('<div class="container" id="info-' + form_idx +  '">' +
                           '<div class="row"><h1>Item '+ form_idx + ' of Order</h1>' +
                           '<i class="toggler fa fa-window-maximize" id="toggle-' + form_idx + '"></i>' +
                           '<i class="remover fa fa-times-circle" id="remove-' + form_idx + '"></i>');

    $('#all_forms').append('<div id="' + formNum + '">');
    $('#' + formNum).append($('#empty_form').html().replace(/__prefix__/g, (form_idx-1).toString()));
    $('#id_form-TOTAL_FORMS').val(form_idx);
});

$(document).on("click", ".toggler", function(e){
    var id = this.id.split("-")[1];
    $('#form-' + id).toggle("fast");
});

$(document).on("click", ".remover", function(e){
    var form_idx = parseInt($('#id_form-TOTAL_FORMS').val()) - 1;
    $('#id_form-TOTAL_FORMS').val(form_idx);
    var id = this.id.split("-")[1];
    $('#info-' + id).remove();
    $('#form-' + id).remove();
});