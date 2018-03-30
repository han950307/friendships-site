$('#add_more').click(function() {
    var form_idx = parseInt($('#id_form-TOTAL_FORMS').val()) + 1;
    var formNum = 'form-' + form_idx;
    $('#all_forms').append('<p class="toggler" id="toggle-' + form_idx + '"> Toggle Item ' + form_idx + '</p>');
    $('#all_forms').append('<div id="' + formNum + '">');
    $('#' + formNum).append('<h1>Item ' + form_idx + ' of Order</h1>');
    $('#' + formNum).append($('#empty_form').html().replace(/__prefix__/g, (form_idx-1).toString()));
    $('#id_form-TOTAL_FORMS').val(form_idx);
});

$(document).on("click", ".toggler", function(e){
    var id = this.id.split("-")[1];
    $('#form-' + id).toggle("fast");
});