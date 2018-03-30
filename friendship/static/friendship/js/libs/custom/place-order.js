$('#add_more').click(function() {
    var form_idx = parseInt($('#id_form-TOTAL_FORMS').val()) + 1;
    $('#all_forms').append('<h1>Item ' + form_idx + ' of Order</h1>')
    $('#all_forms').append($('#empty_form').html().replace(/__prefix__/g, (form_idx-1).toString()));
    $('#id_form-TOTAL_FORMS').val(form_idx);
});