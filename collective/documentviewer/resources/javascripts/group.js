(function($){
$(document).ready(function(){

    var input = $('#search-input input');
    var form = $('#search-input form');
    var cancel = $('#cancel-search');
    var val = input.val()
    if(val != null && val != '' && val != undefined){
        cancel.show();
    }

    form.submit(function(){
        $('#kss-spinner').show();
        $.ajax({
            url: $('base').attr('href'),
            data: {q: input.val()},
            success: function(data){
                var html = $(data);
                $('#pdf-files').replaceWith(html.find('#pdf-files'));
            },
            complete: function(){
                $('#kss-spinner').hide();
            }
        })
        return false;
    });

    cancel.click(function(){
        input.val('');
        form.trigger('submit');
    });

});
})(jQuery);