$(function () {
   $(document).on('click', '.relay-toggle', function (e) {
       e.preventDefault();
       var relay_id = $(this).attr('relay-id');
       var button = $(this);
       $.ajax({
           type: 'GET',
           url: 'switch_relay/',
           dataType: 'json',
           data: {'relay_id': relay_id}
       }).done(function (data) {
           if(data['state'] === 0)
               $(button).removeClass('active');
           else
               $(button).addClass('active');
       }).fail(function (data) {
            $(this).toggleClass('error');
       });
   });
});